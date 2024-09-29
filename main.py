import pygame as pg
from pygame import Vector2, Rect, Surface, time, mouse, image, display
import random

pg.init()
display.set_caption("Ecto-Blast-Em")
mouse.set_visible(False)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
SCREEN = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
SCREEN.fill("Blue")

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


class Projectile:
    rect: Rect
    sprite: Surface
    direction: Vector2
    speed: int
    damage: int
    velocity: Vector2
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
        self.rect = self.rect.move(self.velocity)

    def handle_hit(self):
        pass

    def update(self):
        pass

    def draw(self, background: Surface):
        background.blit(self.sprite, Vector2(self.rect.x, self.rect.y))


class Ectoplasm(Projectile):
    is_collected = False
    distance_traveled = 0
    max_range = 250

    def __init__(self, x, y, direction):
        super().__init__(Rect(x + 8, y + 8, 16, 16),
                         image.load("assets/sprites/player/ectoplasm.png").convert_alpha(),
                         direction,
                         10,
                         5,
                         True)

    def handle_hit(self):
        self.is_active = False

    def update(self):
        center_x = self.rect.centerx
        center_y = self.rect.centery

        if center_y + 8 >= 700:
            self.rect.y = 684
            self.is_active = False

        if center_y - 8 <= 0:
            self.rect.y = 0
            self.is_active = False

        if center_x + 8 >= 1200:
            self.rect.x = 1184
            self.is_active = False

        if center_x - 8 <= 0:
            self.rect.x = 0
            self.is_active = False

        if self.is_active:
            self.distance_traveled += self.direction.magnitude() * self.speed
            super().move()

            if self.distance_traveled >= self.max_range:
                self.is_active = False


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
    max_health = 10
    health = 10
    shoot_pressed: bool = False
    shoot_direction: Vector2 = Vector2(0, -1)
    state = "MOVE"

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @staticmethod
    def get_direction(keys):
        x_strength = int(keys[pg.K_RIGHT]) - int(keys[pg.K_LEFT])
        y_strength = int(keys[pg.K_DOWN]) - int(keys[pg.K_UP])

        direction = Vector2(x_strength, y_strength)
        if x_strength != 0 or y_strength != 0:
            direction = direction.normalize()
        return direction

    def take_damage(self, damage: int):
        self.health -= damage

    def move(self):
        keys = pg.key.get_pressed()
        direction = self.get_direction(keys)
        self.velocity = self.speed * direction
        self.rect = self.rect.move(self.velocity)

        c_pressed = keys[pg.K_c]
        if c_pressed and len(self.ectos) != self.max_num_ecto:
            self.state = "SHOOT"

    def shoot(self):
        keys = pg.key.get_pressed()
        direction = self.get_direction(keys)
        c_pressed = keys[pg.K_c]
        if not c_pressed:
            if direction != V_ZERO:
                ecto = Ectoplasm(self.rect.x, self.rect.y, direction)
                self.ectos.append(ecto)
                self.shoot_pressed = False
                self.num_ecto += 1
            self.state = "MOVE"

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

    def draw(self, background: Surface):
        for ecto in self.ectos:
            ecto.draw(background)
        background.blit(self.sprite, (self.rect.x, self.rect.y))


class Enemy:
    player: Player = Player.get_instance()
    rect: Rect = Rect(0, 0, 50, 50)
    sprite: Surface = Surface((50, 50))
    difficulty = 2
    speed = 1.5
    health = 0
    max_health = 0
    ATTACK_RATE = 0
    last_attack = 0
    velocity: Vector2 = Vector2(0, 0)
    state = "MOVE"
    steer_directions = [V_NORTH, V_NORTH_EAST, V_EAST, V_SOUTH_EAST, V_SOUTH, V_SOUTH_WEST, V_WEST, V_NORTH_WEST]
    dt = 0

    def __init__(self, rect: Rect, sprite: Surface, speed: int, difficulty: int, health: int, ATTACK_RATE: int):
        self.player = Player.get_instance()
        self.rect = rect
        self.sprite = sprite
        self.difficulty = difficulty
        self.health = health
        self.max_health = health
        self.speed = speed
        self.ATTACK_RATE = ATTACK_RATE
        self.sprite.fill("Green")

    def take_damage(self, damage):
        self.health -= damage

    def steer(self, desired_direction, enemies: list, index):
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

        diag_length = 1
        straight_length = 5

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
        desired_velocity = self.steer_directions[best_direction_index] * self.speed
        steering_force = desired_velocity - self.velocity * (random.randint(1, 10) / 10)
        self.velocity += steering_force

    def get_direction_to_player(self):
        dy = self.player.rect.centery - self.rect.centery
        dx = self.player.rect.centerx - self.rect.centerx

        direction = Vector2(dx, dy)

        if dy != 0 or dx != 0:
            direction = direction.normalize()
        return direction

    def move(self):
        self.velocity = self.velocity.normalize() * self.speed
        self.rect = self.rect.move(self.velocity)

    def attack(self):
        pass

    def update(self, dt):
        self.dt = dt
        match self.state:
            case "MOVE":
                self.move()
            case "ATTACK":
                self.attack()

        for e in self.player.ectos:
            if e.rect.colliderect(self.rect) and e.is_active:
                e.handle_hit()
                self.take_damage(e.damage)

    def draw(self, background: Surface):
        background.blit(self.sprite, (self.rect.x, self.rect.y))


class ShooterShot(Projectile):
    player: Player

    def __init__(self, x, y, direction, player):
        super().__init__(Rect(x, y, 16, 16), Surface((16, 16)), direction, 5, 2, True)
        self.sprite.fill("Cyan")
        self.player = player

    def update(self):
        center_x = self.rect.centerx
        center_y = self.rect.centery

        if center_y + 8 >= 700:
            self.rect.y = 684
            self.is_active = False

        if center_y - 8 <= 0:
            self.rect.y = 0
            self.is_active = False

        if center_x + 8 >= 1200:
            self.rect.x = 1184
            self.is_active = False

        if center_x - 8 <= 0:
            self.rect.x = 0
            self.is_active = False

        if self.rect.colliderect(self.player.rect):
            self.player.take_damage(self.damage)
            self.is_active = False

        if self.is_active:
            super().move()

    def draw(self, background: Surface):
        super().draw(background)


class Shooter(Enemy):
    shots: list[ShooterShot] = []

    def __init__(self):
        super().__init__(Rect(0, 0, 25, 25), Surface((25, 25)), 2, 3, 5, 2000)
        self.sprite.fill("Red")

    def move(self):
        super().move()
        self.last_attack += self.dt

        if self.last_attack >= self.ATTACK_RATE:
            self.last_attack = 0
            self.state = "ATTACK"

    def attack(self):
        self.shots.append(
            ShooterShot(self.rect.centerx, self.rect.centery, self.get_direction_to_player(), self.player))
        self.state = "MOVE"

    def update(self, dt):
        super().update(dt)

        shots_to_keep = []
        for s in self.shots:
            s.update()
            if s.is_active:
                shots_to_keep.append(s)

        self.shots = shots_to_keep

    def draw(self, background: Surface):
        super().draw(background)

        for s in self.shots:
            s.draw(background)


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
        e = Shooter()
        return e


class EnemyManager:
    _instance = None
    unspawned_enemies: list[Enemy] = []
    spawned_enemies: list[Enemy] = []
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
                return 5
            case 2:
                return 7
            case 3:
                return 12
            case 4:
                return 18
            case 5:
                return 25

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
            e.steer(e.get_direction_to_player(), self.spawned_enemies, i)
            e.update(dt)
            if e.health > 0:
                enemies_to_keep.append(e)

        self.spawned_enemies = enemies_to_keep
        self.last_spawn += dt

        len_unspawned = len(self.unspawned_enemies)
        len_spawned = len(self.spawned_enemies)

        if self.last_spawn >= self.spawn_rate and len_unspawned > 0:
            self.spawned_enemies.append(self.unspawned_enemies.pop(0))
            self.last_spawn = 0

        if len_unspawned <= 0 and len_spawned <= 0:
            self.wave_complete = True

    def draw(self, background: Surface):
        for e in self.spawned_enemies:
            e.draw(background)


class Upgrade:
    player = None
    cost = 0
    rect: Rect = None
    card: Surface = None
    clicked = False
    bought = False
    sold_card = image.load("assets/UI/sold_card.png").convert_alpha()

    def __init__(self):
        self.rect = Rect(0, 0, 200, 200)
        self.player = Player.get_instance()

    def set_position(self, position: tuple):
        self.rect.x = position[0]
        self.rect.y = position[1]

    def update(self):
        pass

    def draw(self, background: Surface):
        if self.bought:
            background.blit(self.sold_card, (self.rect.x, self.rect.y))
        else:
            background.blit(self.card, (self.rect.x, self.rect.y))


# IMPLEMENT UPGRADES BELOW THIS LINE
class MaxHealthUpgrade(Upgrade):
    def __init__(self):
        super().__init__()
        self.cost = 5
        self.card = image.load("assets/UI/mhu_card.png").convert_alpha()

    def update(self):
        if self.bought or not self.rect.collidepoint(mouse.get_pos()):
            self.clicked = False
            return

        pressed = mouse.get_pressed()[0]
        if pressed:
            self.clicked = True
            time.wait(120)

        if self.clicked and not pressed:
            if self.player.num_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.player.max_health += 1
                self.bought = True
            self.clicked = False

    def draw(self, background: Surface):
        super().draw(background)


class NumEctoUpgrade(Upgrade):
    def __init__(self):
        super().__init__()
        self.cost = 5
        self.card = image.load("assets/UI/neu_card.png").convert_alpha()

    def update(self):
        if self.bought or not self.rect.collidepoint(mouse.get_pos()):
            self.clicked = False
            return

        pressed = mouse.get_pressed()[0]

        if pressed:
            self.clicked = True
            time.wait(120)

        if self.clicked and not pressed:
            if self.player.num_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.player.max_num_ecto += 1
                self.bought = True
            self.clicked = False

    def draw(self, background: Surface):
        super().draw(background)


class RestoreHealthUpgrade(Upgrade):
    def __init__(self):
        super().__init__()
        self.cost = 10
        self.card = image.load("assets/UI/rhu_card.png").convert_alpha()

    def update(self):
        if self.bought or not self.rect.collidepoint(mouse.get_pos()):
            self.clicked = False
            return

        pressed = mouse.get_pressed()[0]

        if pressed:
            self.clicked = True
            time.wait(120)

        if self.clicked and not pressed:
            if self.player.num_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.player.health = self.player.max_health
                self.bought = True
            self.clicked = False

    def draw(self, background: Surface):
        super().draw(background)


class Shop:
    _instance = None
    rect = Rect(200, 200, 600, 200)

    upgrades: list[Upgrade] = [
        MaxHealthUpgrade(),
        NumEctoUpgrade(),
        RestoreHealthUpgrade()
    ]

    upgrade_1 = None
    upgrade_2 = None
    upgrade_3 = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def rand_upgrade(self) -> Upgrade:
        return self.upgrades.pop(random.randint(0, len(self.upgrades) - 1))

    def get_upgrades(self):
        self.upgrade_1 = self.rand_upgrade()
        self.upgrade_2 = self.rand_upgrade()
        self.upgrade_3 = self.rand_upgrade()

        self.upgrade_1.set_position(self.rect.topleft)
        self.upgrade_2.set_position(self.rect.midtop)
        self.upgrade_3.set_position(self.rect.topright)

    def close(self):
        self.upgrade_1.bought = False
        self.upgrade_2.bought = False
        self.upgrade_3.bought = False

        self.upgrades.append(self.upgrade_1)
        self.upgrades.append(self.upgrade_2)
        self.upgrades.append(self.upgrade_3)

    def update(self):
        self.upgrade_1.update()
        self.upgrade_2.update()
        self.upgrade_3.update()

    def draw(self, background):
        self.upgrade_1.draw(background)
        self.upgrade_2.draw(background)
        self.upgrade_3.draw(background)


class UI:
    game = None
    width = 0
    height = 0
    surf: Surface = None
    rect: Rect = None
    player = None

    def __init__(self):
        self.player = Player.get_instance()
        self.width = WINDOW_WIDTH
        self.height = 100
        self.surf = Surface((self.width, self.height))
        self.surf.fill("Red")

    def update(self):
        pass

    def draw(self):
        pass


class Game:
    _instance = None
    player = None
    enemy_manager = None
    shop = None
    RUNNING = True
    curr_wave = 1
    MAX_WAVES = 3
    background: Surface = Surface((WINDOW_WIDTH, WINDOW_HEIGHT - 100))
    clock = time.Clock()
    state = "HOME"
    prev_state = "WAVE"
    cursor = None
    cursor_rect = Rect(0, 0, 16, 16)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def restart_game(self):
        # TODO IMPLEMENT PROPERLY
        self.curr_wave = 1
        self.enemy_manager.load_enemies(self.curr_wave)
        self.player.rect.x = 0
        self.player.rect.y = 0
        self.state = "WAVE"

    def update(self):
        dt = self.clock.get_time()
        keys = pg.key.get_pressed()

        match self.state:
            case "HOME":
                self.state = "INFO"

            case "WAVE":
                if keys[pg.K_i]:
                    self.state = "INFO"
                    self.prev_state = "WAVE"

                self.player.update()
                self.enemy_manager.update(dt)

                if self.player.health < 0:
                    self.state = "GAME_OVER"

                if self.enemy_manager.wave_complete:
                    self.player.rect.x = (WINDOW_WIDTH / 2) - 16
                    self.player.rect.y = (WINDOW_HEIGHT / 2) - 16
                    self.player.num_ecto = 0
                    self.player.ectos = []

                    if self.curr_wave < self.MAX_WAVES:
                        self.shop.get_upgrades()
                        self.state = "SHOP"
                    else:
                        self.state = "GAME_OVER"

            case "SHOP":
                if keys[pg.K_i]:
                    self.state = "INFO"
                    self.prev_state = "SHOP"

                if keys[pg.K_SPACE]:
                    self.shop.close()
                    self.curr_wave += 1
                    self.enemy_manager.load_enemies(self.curr_wave)
                    self.state = "WAVE"

                self.shop.update()

            case "INFO":
                if keys[pg.K_e]:
                    self.state = self.prev_state

            case "GAME_OVER":
                if keys[pg.K_SPACE]:
                    self.restart_game()
                if keys[pg.K_e]:
                    self.RUNNING = False

        # TODO Update the UI

    def draw(self):
        match self.state:
            case "WAVE":
                SCREEN.blit(self.background, (0, 0))
                self.background.fill("Black")
                self.player.draw(self.background)
                self.enemy_manager.draw(self.background)

            case "SHOP":
                SCREEN.blit(self.background, (0, 0))
                self.background.fill("Black")
                self.shop.draw(self.background)
                SCREEN.blit(self.cursor, mouse.get_pos())

            case "INFO":
                # TODO CREATE INFO SCREEN
                SCREEN.blit(self.background, (0, 0))
                self.background.fill("Cyan")

            case "GAME_OVER":
                # TODO CREATE GAME OVER SCREEN
                # TODO Show Victory or Defeat Screen Based on Player Health
                SCREEN.blit(self.background, (0, 0))
                self.background.fill("Green")

        # TODO Draw the UI
        display.flip()

    def start(self) -> None:
        self.player = Player.get_instance()
        self.enemy_manager = EnemyManager.get_instance()
        self.shop = Shop().get_instance()
        self.enemy_manager.load_enemies(self.curr_wave)
        self.cursor = image.load("assets/sprites/player/cursor.png").convert_alpha()

        while self.RUNNING:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    self.RUNNING = False

            if self.RUNNING:
                self.update()
                self.draw()
                self.clock.tick(60)


if __name__ == "__main__":
    Game.get_instance().start()
