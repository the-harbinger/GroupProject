import math

import pygame as pg
import sys

import pygame.display
from pygame.locals import *
from pygame import Vector2, Rect, Surface, Color, time, mouse, image, display, mixer
import random

# GLOBALS
pg.init()
display.set_caption("Ecto-Blast-Em")
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
SCREEN = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
SCREEN.fill("Black")
GAME_HEIGHT = WINDOW_HEIGHT - 80
GAME_WIDTH = WINDOW_WIDTH
GAME_RECT = Rect(0, 0, GAME_WIDTH, GAME_HEIGHT)
GAME_BACKGROUND: Surface = Surface((GAME_WIDTH, GAME_HEIGHT))

mixer.init()
mixer.pre_init()
atmosphere_sound = mixer.Sound("assets/sounds/horror_atmosphere_0.wav")
atmosphere_sound.set_volume(0.35)
ecto_shoot_sound = mixer.Sound("assets/sounds/ecto_shoot_0.wav")
atmosphere_sound.play(-1)

mouse.set_visible(False)
CURSOR_RECT = Rect(0, 0, 32, 32)
CURSOR = image.load("assets/sprites/player/cursor.png").convert_alpha()

TICK_RATE = 60

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

V_ZERO = Vector2(0, 0)
V_NORTH = Vector2(0, -1)
V_NORTH_EAST = Vector2(1, -1)
V_EAST = Vector2(1, 0)
V_SOUTH_EAST = Vector2(1, 1)
V_SOUTH = Vector2(0, 1)
V_SOUTH_WEST = Vector2(-1, 1)
V_WEST = Vector2(-1, 0)
V_NORTH_WEST = Vector2(-1, -1)


def create_line(x1, y1, x2, y2):
    return (x1, y1), (x2, y2)


def check_wall_collision(rect: Rect) -> bool:
    collides: bool = False

    if rect.bottom >= GAME_HEIGHT:
        rect.y = GAME_HEIGHT - rect.h
        collides = True

    if rect.top <= 0:
        rect.y = 0
        collides = True

    if rect.right >= GAME_WIDTH:
        rect.x = GAME_WIDTH - rect.width
        collides = True

    if rect.left <= 0:
        collides = True
        rect.x = 0

    return collides


def get_rand_point_for_rect(rect: Rect) -> Vector2:
    return Vector2(random.randint(0, GAME_WIDTH - rect.width), random.randint(0, GAME_HEIGHT - rect.height))


def generate_empty_grid(num_rows: int, num_cols: int) -> list[list]:
    grid = []
    for i in range(num_rows):
        row = [None for _ in range(num_cols)]
        grid.append(row)

    return grid


class Projectile:
    rect: Rect
    sprite: Surface
    direction: Vector2
    speed: int
    damage: int
    velocity: Vector2 = V_ZERO
    is_active: bool

    def __init__(self, rect: Rect, sprite: Surface, direction: Vector2, speed: int, damage: int, is_active: bool):
        self.rect = rect
        self.sprite = sprite
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.is_active = is_active

    def move(self):
        self.velocity = self.direction * self.speed
        self.rect.centerx += self.velocity.x
        self.rect.centery += self.velocity.y

    def handle_hit(self):
        pass

    def update(self):
        pass

    def draw(self):
        GAME_BACKGROUND.blit(self.sprite, (self.rect.x, self.rect.y))


class Ectoplasm(Projectile):
    is_collected = False
    distance_traveled = 0
    max_range = 250
    damage = 5

    def __init__(self, direction, center):
        rect = Rect(0, 0, 16, 16)
        rect.center = center
        super().__init__(rect,
                         image.load("assets/sprites/player/ectoplasm.png").convert_alpha(),
                         direction,
                         10,
                         5,
                         True)
        self.damage = 5

    def handle_hit(self):
        self.is_active = False

    def update(self):
        self.distance_traveled += self.velocity.magnitude()
        if self.distance_traveled >= self.max_range or check_wall_collision(self.rect):
            self.is_active = False
        if self.is_active:
            super().move()


class Player:
    _instance = None
    rect = Rect(600, 400, 32, 32)
    sprite = image.load("assets/sprites/player/ghost_player.png").convert_alpha()
    velocity = Vector2(0, 0)
    ectos: list[Ectoplasm] = []
    speed = 5
    num_coins = 15
    num_ecto = 0
    max_num_ecto = 5
    phase_speed_modifier = 1.5
    phase_time = 0.33
    max_health = 20
    health = max_health
    shoot_pressed = False
    shoot_direction: Vector2
    state = "MOVE"
    guide_width = 16
    hurt_sound: mixer.Sound = mixer.Sound("assets/sounds/player_hurt_0.mp3")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.rect.center = GAME_RECT.center

        return cls._instance

    @staticmethod
    def __get_direction(keys):
        x_strength = (int(keys[K_RIGHT]) + int(keys[K_d])) - (int(keys[K_LEFT]) + int(keys[K_a]))
        y_strength = (int(keys[K_DOWN]) + int(keys[K_s])) - (int(keys[K_UP] + int(keys[K_w])))

        direction = Vector2(x_strength, y_strength)
        if direction.length() != 0:
            direction = direction.normalize()
        return direction

    def take_damage(self, damage: int):
        self.health -= damage

    def move(self):
        keys = pg.key.get_pressed()
        direction = self.__get_direction(keys)
        self.velocity = self.speed * direction
        self.rect = self.rect.move(self.velocity)

        check_wall_collision(self.rect)

        shoot_pressed = mouse.get_pressed()[0]
        if shoot_pressed and self.num_ecto < self.max_num_ecto:
            self.state = "SHOOT"

    def shoot(self):
        shoot_pressed = mouse.get_pressed()[0]
        dx = CURSOR_RECT.centerx - self.rect.centerx
        dy = CURSOR_RECT.centery - self.rect.centery

        direction = Vector2(dx, dy)
        if direction.length() != 0:
            direction = direction.normalize()

        if not shoot_pressed:
            ecto = Ectoplasm(direction, self.rect.center)
            self.ectos.append(ecto)
            ecto_shoot_sound.play()
            self.shoot_pressed = False
            self.num_ecto += 1
            self.state = "MOVE"

    def __draw_guide(self):
        start_point = Vector2(self.rect.center)
        end_point = Vector2(CURSOR_RECT.center)
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y

        direction = Vector2(dx, dy)
        if direction.length() != 0:
            direction = direction.normalize()

        end_point = (direction * Ectoplasm.max_range) + start_point
        pg.draw.line(GAME_BACKGROUND, Color(255, 255, 255), start_point, end_point, self.guide_width)

    def update(self):
        match self.state:
            case "MOVE":
                self.move()
            case "SHOOT":
                self.shoot()

        uncollected_ectos = []
        for ecto in self.ectos:
            if ecto.rect.colliderect(self.rect) and not ecto.is_active:
                ecto.is_collected = True
                self.num_ecto -= 1

            ecto.update()

            if not ecto.is_collected:
                uncollected_ectos.append(ecto)
            self.ectos = uncollected_ectos

    def draw(self):
        for ecto in self.ectos:
            ecto.draw()

        if self.state == "SHOOT":
            self.__draw_guide()
        GAME_BACKGROUND.blit(self.sprite, (self.rect.x, self.rect.y))


class Enemy:
    player: Player = Player.get_instance()
    rect: Rect = Rect(0, 0, 50, 50)
    sprite: Surface = Surface((50, 50))
    difficulty = 2
    speed = 2
    health = 0
    max_health = 0
    attack_rate = 0
    last_attack = 0
    telegraph_time = 0
    telegraph_timer = 0
    velocity: Vector2 = V_ZERO
    state = "MOVE"
    steer_directions = [V_NORTH, V_NORTH_EAST, V_EAST, V_SOUTH_EAST, V_SOUTH, V_SOUTH_WEST, V_WEST, V_NORTH_WEST]
    dt = 0

    def __init__(self, w, h, sprite: Surface, speed: int, difficulty: int, health: int, attack_rate: int,
                 outside_spawn: bool, telegraph_time: int):
        if outside_spawn:
            side = random.randint(1, 4)
            x = 0
            y = 0

            match side:
                case 1:
                    y = random.randint(0, GAME_HEIGHT)
                case 2:
                    x = random.randint(0, GAME_WIDTH)
                case 3:
                    x = random.randint(0, GAME_WIDTH)
                    y = GAME_HEIGHT
                case 4:
                    x = GAME_WIDTH
                    y = random.randint(0, GAME_HEIGHT)
            self.rect = Rect(x, y, w, h)

        self.sprite = sprite
        self.difficulty = difficulty
        self.health = health
        self.max_health = health
        self.speed = speed
        self.attack_rate = attack_rate
        self.telegraph_time = telegraph_time
        self.sprite.fill("Green")

    def take_damage(self, damage):
        self.health -= damage

    def steer(self, enemies: list, index):
        desired_direction = self.get_direction_to_player()
        interest_weights = []
        danger_weights = [0, 0, 0, 0, 0, 0, 0, 0]
        for steer_dir in self.steer_directions:
            interest_weights.append(desired_direction.dot(steer_dir))

        mt = self.rect.midtop
        tr = self.rect.topright
        mr = self.rect.midright
        br = self.rect.bottomright
        mb = self.rect.midbottom
        bl = self.rect.bottomleft
        ml = self.rect.midleft
        tl = self.rect.topleft

        diag_length = 3
        straight_length = 7

        steer_rays = [
            create_line(mt[0], mt[1], mt[0], mt[1] - straight_length),
            create_line(tr[0], tr[1], tr[0] + diag_length, tr[1] - diag_length),
            create_line(mr[0], mr[1], mr[0] + straight_length, mr[1]),
            create_line(br[0], br[1], br[0] + diag_length, br[1] + 5),
            create_line(mb[0], mb[1], mb[0], mb[1] + straight_length),
            create_line(bl[0], bl[1], bl[0] - diag_length, bl[1] + diag_length),
            create_line(ml[0], ml[1], ml[0] - straight_length, ml[1]),
            create_line(tl[0], tl[1], tl[0] - diag_length, tl[1] - diag_length)
        ]

        for i in range(8):
            for j in range(len(enemies)):
                if j == index:
                    continue
                enemy_2: Enemy = enemies[j]
                ray = steer_rays[i]
                if enemy_2.rect.clipline(ray) != ():
                    danger_weights[i] += 5
                    danger_weights[(i - 1 + 8) % 8] += 2
                    danger_weights[(i + 1) % 8] += 2

        steer_map = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        best_direction_index = 0
        for i in range(8):
            interest = interest_weights[i] - danger_weights[i]
            steer_map[i] = interest
            if steer_map[best_direction_index] < interest:
                best_direction_index = i
        desired_velocity = (self.steer_directions[best_direction_index] + desired_direction)
        if desired_velocity.length() != 0:
            desired_velocity = desired_velocity.normalize() * self.speed
        steering_force = desired_velocity - self.velocity
        self.velocity += steering_force

    def get_direction_to_player(self):
        dy = self.player.rect.centery - self.rect.centery
        dx = self.player.rect.centerx - self.rect.centerx

        direction = Vector2(dx, dy)

        if direction.length() != 0:
            direction = direction.normalize()
        return direction

    def get_distance_to_player(self):
        return math.sqrt((abs(self.player.rect.centery - self.rect.centery)**2) +
                         (abs(self.player.rect.centerx - self.rect.centerx)**2))

    def move(self):
        if self.velocity.length() != 0:
            self.velocity = self.velocity.normalize() * self.speed
        self.rect = self.rect.move(self.velocity)
        check_wall_collision(self.rect)

    def attack(self):
        pass

    def telegraph(self):
        self.telegraph_timer += self.dt
        self.sprite.fill("Cyan")
        if self.telegraph_timer >= self.telegraph_time:
            self.telegraph_timer = 0
            self.sprite.fill("Green")
            self.state = "ATTACK"

    def update(self, dt):
        self.dt = dt
        match self.state:
            case "MOVE":
                self.move()
            case "ATTACK":
                self.attack()
            case "TELEGRAPH":
                self.telegraph()

        for e in self.player.ectos:
            if e.rect.colliderect(self.rect) and e.is_active:
                e.handle_hit()
                self.take_damage(e.damage)

    def draw(self):
        GAME_BACKGROUND.blit(self.sprite, (self.rect.x, self.rect.y))


class Dasher(Enemy):
    dash_speed = 15
    base_speed = 2
    max_dash_distance = 300
    dash_distance = 0
    dash_time = 250
    dash_timer = 0
    dash_direction: Vector2 = V_ZERO
    dash_range = 275
    delt_damage = False

    def __init__(self):
        w = 25
        h = 25
        super().__init__(w, h, Surface((w, h)), 2, 2, 5, 2000, True, 400)

    def move(self):
        self.speed = self.base_speed
        super().move()
        self.last_attack += self.dt

        if self.last_attack >= self.attack_rate and self.get_distance_to_player() <= self.dash_range:
            self.dash_direction = self.get_direction_to_player()
            self.state = "TELEGRAPH"
            self.last_attack = 0

    def attack(self):
        self.speed = self.dash_speed
        self.velocity = self.dash_direction * self.speed

        super().move()
        self.dash_distance += self.velocity.magnitude()

        if not self.delt_damage and self.rect.colliderect(self.player.rect):
            self.delt_damage = True
            self.player.health -= 1

        if self.dash_distance >= self.max_dash_distance:
            self.delt_damage = False
            self.dash_distance = 0
            self.state = "MOVE"


class EnemyProjectile(Projectile):
    player: Player = Player.get_instance()

    def __init__(self, center, direction):
        rect = Rect(0, 0, 16, 16)
        rect.center = center
        super().__init__(rect,
                         image.load("assets/sprites/enemy/enemy_projectile.png").convert_alpha(),
                         direction,
                         5,
                         2,
                         True)

    def update(self):
        if self.is_active:
            if check_wall_collision(self.rect):
                self.is_active = False

            if self.rect.colliderect(self.player.rect):
                self.is_active = False
                self.player.take_damage(self.damage)

        if self.is_active:
            super().move()


class Shooter(Enemy):
    projectiles: list[EnemyProjectile] = []

    def __init__(self):
        w = 25
        h = 25
        super().__init__(w, h, Surface((w, h)), 2, 3, 5, 2500, True, 0)
        self.sprite.fill("Red")

    def move(self):
        if self.get_distance_to_player() <= 250:
            self.velocity -= self.get_direction_to_player() * self.speed * 2

        super().move()
        self.last_attack += self.dt

        if self.last_attack >= self.attack_rate:
            self.last_attack = 0
            self.state = "ATTACK"

    def attack(self):
        self.projectiles.append(EnemyProjectile(self.rect.center, self.get_direction_to_player()))
        self.state = "MOVE"

    def update(self, dt):
        super().update(dt)

        projectiles_to_keep = []
        for s in self.projectiles:
            s.update()
            if s.is_active:
                projectiles_to_keep.append(s)

        self.projectiles = projectiles_to_keep

    def draw(self):
        super().draw()
        for s in self.projectiles:
            s.draw()


class EnemyFactory:
    _instance = None
    enemy_types = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def create_enemy(cls) -> Enemy:
        rand_int = random.randint(1, 2)
        match rand_int:
            case 1:
                return Shooter()
            case 2:
                return Dasher()


class EnemyManager:
    _instance = None
    unspawned_enemies: list[Enemy] = []
    spawned_enemies: list[Enemy] = []
    dead_projectiles: list[EnemyProjectile] = []
    difficulty = 0
    spawn_rate = 0
    last_spawn = 0
    wave_complete = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @staticmethod
    def __get_difficulty(curr_wave: int):
        match curr_wave:
            case 1:
                return 2
            case 2:
                return 17
            case 3:
                return 22
            case 4:
                return 28
            case 5:
                return 35

    @staticmethod
    def __get_spawn_rate(curr_wave: int):
        match curr_wave:
            case 1:
                return 900
            case 2:
                return 800
            case 3:
                return 700
            case 4:
                return 600
            case 5:
                return 500

    def load_enemies(self, curr_wave: int):
        self.spawn_rate = self.__get_spawn_rate(curr_wave)
        self.difficulty = self.__get_difficulty(curr_wave)
        self.last_spawn = 0
        self.wave_complete = False

        while self.difficulty > 0:
            e = EnemyFactory.create_enemy()
            self.unspawned_enemies.append(e)
            self.difficulty -= e.difficulty

    def update(self, dt: int):
        enemies_to_keep: list[Enemy] = []
        for i in range(len(self.spawned_enemies)):
            e = self.spawned_enemies[i]
            e.steer(self.spawned_enemies, i)
            e.update(dt)

            if e.health > 0:
                enemies_to_keep.append(e)
            elif e.__class__ == Shooter:
                self.dead_projectiles = self.dead_projectiles + e.projectiles

        keep_projectiles = []
        for p in self.dead_projectiles:
            p.update()
            if p.is_active:
                keep_projectiles.append(p)

        self.dead_projectiles = keep_projectiles
        self.spawned_enemies = enemies_to_keep
        self.last_spawn += dt

        len_unspawned = len(self.unspawned_enemies)
        len_spawned = len(self.spawned_enemies)

        if self.last_spawn >= self.spawn_rate and len_unspawned > 0:
            self.spawned_enemies.append(self.unspawned_enemies.pop(0))
            self.last_spawn = 0

        if len_unspawned <= 0 and len_spawned <= 0:
            self.wave_complete = True

    def draw(self):
        for e in self.spawned_enemies:
            e.draw()

        for p in self.dead_projectiles:
            p.draw()


class Hazard:
    player: Player = Player.get_instance()
    rect: Rect
    sprite: Surface
    state: str = "ACTIVE"

    def __init__(self, x, y, w, h):
        self.rect = Rect(x, y, w, h)
        self.sprite = Surface((w, h))
        self.sprite.fill("darkviolet")

    def active(self):
        pass

    def inactive(self):
        pass

    def update(self):
        match self.state:
            case "ACTIVE":
                self.active()
            case "INACTIVE":
                self.inactive()

    def draw(self):
        GAME_BACKGROUND.blit(self.sprite, (self.rect.x, self.rect.y))


class HazardManager:
    _instance = None
    grid_size = tuple([15, 31])
    hazards: list[Hazard] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def load_hazards(self):
        self.hazards = []
        for row_ind in range(1, self.grid_size[0]):
            for col_ind in range(1, self.grid_size[1]):
                rand_num = random.randint(0, 64)
                if rand_num == 64:
                    self.hazards.append(Hazard(col_ind * 40, row_ind * 40, 40, 40))

    def update(self):
        pass

    def draw(self):
        for h in self.hazards:
            h.draw()


class Upgrade:
    player = Player.get_instance()
    cost: int
    rect: Rect
    card: Surface
    sold_card = image.load("assets/UI/sold_card.png").convert_alpha()
    highlight = Surface((200, 200))
    highlight_rect: Rect
    highlight.fill("white")
    clicked = False
    bought = False
    hovered = False
    hover_offset = 10

    def __init__(self, cost: int, card: Surface):
        self.rect = Rect(0, 0, 200, 200)
        self.highlight_rect = Rect(0, 0, 200, 200)
        self.card = card
        self.cost = cost

    def set_shop_position(self, position: tuple):
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.highlight_rect.x = position[0]
        self.highlight_rect.y = position[1]

    def apply_upgrade(self):
        pass

    def update(self):
        self.hovered = self.highlight_rect.collidepoint(mouse.get_pos())
        if self.bought or not self.hovered:
            self.clicked = False
            return

        pressed = mouse.get_pressed()[0]

        if pressed:
            self.clicked = True
            time.wait(120)

        if self.clicked and not pressed:
            if self.player.num_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.bought = True
                self.apply_upgrade()
            self.clicked = False

    def draw(self):
        if self.hovered:
            self.rect.x = self.highlight_rect.x + self.hover_offset
            self.rect.y = self.highlight_rect.y - self.hover_offset
            GAME_BACKGROUND.blit(self.highlight, (self.highlight_rect.x, self.highlight_rect.y))
        else:
            self.rect.x = self.highlight_rect.x
            self.rect.y = self.highlight_rect.y

        if self.bought:
            GAME_BACKGROUND.blit(self.sold_card, (self.rect.x, self.rect.y))
        else:
            GAME_BACKGROUND.blit(self.card, (self.rect.x, self.rect.y))


# UPGRADES BELOW THIS LINE
class MaxHealthUpgrade(Upgrade):
    def __init__(self):
        super().__init__(5, image.load("assets/UI/max_health_upgrade_card.png").convert())

    def apply_upgrade(self):
        self.player.max_health += 1
        self.player.health += 1


class NumEctoUpgrade(Upgrade):
    def __init__(self):
        super().__init__(5, image.load("assets/UI/num_ectoplasm_upgrade_card.png").convert())

    def apply_upgrade(self):
        self.player.max_num_ecto += 1


class EctoRangeUpgrade(Upgrade):
    def __init__(self):
        super().__init__(5, image.load("assets/UI/ectoplasm_range_upgrade_card.png").convert())

    def apply_upgrade(self):
        Ectoplasm.max_range *= 1.1


class RestoreHealthUpgrade(Upgrade):
    def __init__(self):
        super().__init__(10, image.load("assets/UI/restore_health_upgrade_card.png").convert())

    def apply_upgrade(self):
        self.player.health = self.player.max_health


class PlayerSpeedUpgrade(Upgrade):
    def __init__(self):
        super().__init__(7, image.load("assets/UI/player_speed_upgrade_card.png").convert())

    def apply_upgrade(self):
        self.player.speed += 1


class EctoDamageUpgrade(Upgrade):
    def __init__(self):
        super().__init__(5, image.load("assets/UI/ectoplasm_damage_upgrade_card.png").convert())

    def apply_upgrade(self):
        Ectoplasm.damage += 1


class Shop:
    _instance = None
    rect: Rect

    all_upgrades: list[Upgrade] = [
        MaxHealthUpgrade(),
        NumEctoUpgrade(),
        RestoreHealthUpgrade(),
        EctoRangeUpgrade(),
        PlayerSpeedUpgrade(),
        EctoDamageUpgrade()
    ]

    shop_upgrades: list[Upgrade] = []
    positions: list[tuple]

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.rect = Rect(200, 200, GAME_WIDTH, 200)
            cls.rect.center = GAME_RECT.center
            y_pos = cls.rect.y
            centerx = GAME_RECT.centerx
            cls.positions: list[tuple] = [tuple([centerx - 400, y_pos]),
                                          tuple([centerx - 100, y_pos]),
                                          tuple([centerx + 200, y_pos])]
        return cls._instance

    def get_rand_upgrade(self) -> Upgrade:
        return self.all_upgrades.pop(random.randint(0, len(self.all_upgrades) - 1))

    def set_upgrades(self):
        for i in range(3):
            self.shop_upgrades.append(self.get_rand_upgrade())
            self.shop_upgrades[i].set_shop_position(self.positions[i])

    def close(self):
        for upgrade in self.shop_upgrades:
            upgrade.bought = False
            self.all_upgrades.append(upgrade)
        self.shop_upgrades = []

    def update(self):
        for upgrade in self.shop_upgrades:
            upgrade.update()

    def draw(self):
        for upgrade in self.shop_upgrades:
            upgrade.draw()


class GameUI:
    font = pygame.font.Font("assets/UI/fonts/cambria-bold.ttf", 50)

    # Load ectoplasm image
    ectoplasm_image = pygame.image.load('assets/sprites/player/ectoplasm.png').convert_alpha()
    ectoplasm_image = pygame.transform.scale(ectoplasm_image, (50, 50))

    def __init__(self):
        self.player = Player.get_instance()

    def draw_health_bar(self, surface, x, y):
        max_health = self.player.max_health
        bar_width = 200
        bar_height = 50

        # Health bar background
        pygame.draw.rect(surface, RED, (x, y, bar_width, bar_height))

        # Health bar foreground (based on current health)
        current_health_width = (self.player.health / max_health) * bar_width
        pygame.draw.rect(surface, GREEN, (x, y, current_health_width, bar_height))

    def draw_coin_counter(self, surface, x, y):
        text = self.font.render(f"Coins: {self.player.num_coins}", True, WHITE)
        surface.blit(text, (x, y))

    def draw_ectoplasm(self, surface, x, y):
        surface.blit(self.ectoplasm_image, (x, y))


class Game:
    _instance = None
    player = None
    enemy_manager = None
    hazard_manager = None
    shop = None
    RUNNING = True
    curr_wave = 1
    MAX_WAVES = 3
    clock = time.Clock()
    state = "HOME"
    prev_state = "WAVE"
    game_ui: GameUI
    info_screen = image.load("assets/UI/info_screen.png").convert()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def restart_game(self):
        # TODO IMPLEMENT PROPERLY
        self.curr_wave = 1
        self.enemy_manager.load_enemies(self.curr_wave)
        self.player.rect.center = GAME_RECT.center
        self.state = "WAVE"

    def update(self):
        dt = self.clock.get_time()
        keys = pg.key.get_pressed()

        match self.state:
            case "HOME":
                self.state = "INFO"

            case "WAVE":
                if keys[K_i]:
                    self.state = "INFO"
                    self.prev_state = "WAVE"

                self.player.update()
                self.enemy_manager.update(dt)

                if self.player.health <= 0:
                    self.state = "GAME_OVER"

                if self.enemy_manager.wave_complete:
                    self.player.rect.centerx = GAME_RECT.centerx
                    self.player.rect.centery = GAME_RECT.centery
                    self.player.num_ecto = 0
                    self.player.ectos = []
                    self.enemy_manager.dead_projectiles = []

                    if self.curr_wave < self.MAX_WAVES:
                        self.shop.set_upgrades()
                        self.state = "SHOP"
                    else:
                        self.state = "GAME_OVER"

            case "SHOP":
                if keys[K_i]:
                    self.state = "INFO"
                    self.prev_state = "SHOP"

                if keys[K_SPACE]:
                    self.shop.close()
                    self.curr_wave += 1
                    self.enemy_manager.load_enemies(self.curr_wave)
                    self.hazard_manager.load_hazards()
                    self.state = "WAVE"

                self.shop.update()

            case "INFO":
                if keys[K_e]:
                    self.state = self.prev_state

            case "GAME_OVER":
                if keys[K_SPACE]:
                    self.restart_game()
                if keys[K_e]:
                    self.RUNNING = False

    def draw(self):
        match self.state:
            case "WAVE":
                SCREEN.blit(GAME_BACKGROUND, (0, 0))
                GAME_BACKGROUND.fill("Black")
                self.hazard_manager.draw()
                self.player.draw()
                self.enemy_manager.draw()

            case "SHOP":
                SCREEN.blit(GAME_BACKGROUND, (0, 0))
                GAME_BACKGROUND.fill("Black")
                self.shop.draw()

            case "INFO":
                SCREEN.blit(self.info_screen, (0, 0))

            case "GAME_OVER":
                if self.player.health > 0:
                    SCREEN.blit(image.load("assets/UI/congratulations.png"), (0, 0))
                else:
                    SCREEN.blit(image.load("assets/UI/you_died.png"), (0, 0))

        mouse_pos = mouse.get_pos()
        CURSOR_RECT.x = mouse_pos[0]
        CURSOR_RECT.y = mouse_pos[1]
        SCREEN.blit(CURSOR, (CURSOR_RECT.x, CURSOR_RECT.y))
        display.flip()

    def start(self) -> None:
        self.player = Player.get_instance()
        self.enemy_manager = EnemyManager.get_instance()
        self.shop = Shop().get_instance()
        self.enemy_manager.load_enemies(self.curr_wave)
        self.game_ui = GameUI()
        self.hazard_manager = HazardManager.get_instance()
        self.hazard_manager.load_hazards()

        while self.RUNNING:
            for e in pg.event.get():
                if e.type == QUIT:
                    pg.quit()
                    sys.exit()
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        pg.quit()
                        sys.exit()

            self.update()
            self.draw()

            SCREEN.fill("darkslategrey")
            # Draw the UI elements in a horizontal line
            y_position = GAME_HEIGHT + 15  # Keep the same Y position for all elements

            # Starting X positions for the elements
            x_health_bar = 50
            x_coin_counter = x_health_bar + 300  # Adjust spacing after health bar
            x_ectoplasm = x_coin_counter + 300  # Adjust spacing after coin counter

            # Draw the health bar
            self.game_ui.draw_health_bar(SCREEN, x_health_bar, y_position)

            # Draw the coin counter
            self.game_ui.draw_coin_counter(SCREEN, x_coin_counter, y_position)

            # Draw the ectoplasm image
            self.game_ui.draw_ectoplasm(SCREEN, x_ectoplasm, y_position)

            self.clock.tick(TICK_RATE)


if __name__ == "__main__":
    Game.get_instance().start()
