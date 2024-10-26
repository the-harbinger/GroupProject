import math

import pygame as pg
import sys

import pygame.display
from pygame.locals import *
from pygame import Vector2, Rect, Surface, Color, time, mouse, image, display, mixer
import random

# GLOBALS
pg.init()
WHITE = (255, 255, 255)
HEALTHBAR_LOWER_COLOR = (124, 60, 92)
HEALTHBAR_HIGHER_COLOR = (0, 172, 252)
DARK_BLUE = (0, 103, 139)
BG_COLOR = "Black"
SCREEN_COLOR = DARK_BLUE
display.set_caption("Ecto-Blast-Em")
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
SCREEN = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
SCREEN.fill(SCREEN_COLOR)
GAME_HEIGHT = WINDOW_HEIGHT - 80
GAME_WIDTH = WINDOW_WIDTH
GAME_RECT = Rect(0, 0, GAME_WIDTH, GAME_HEIGHT)
GAME_BACKGROUND: Surface = Surface((GAME_WIDTH, GAME_HEIGHT))
KEYS = pg.key.get_pressed()

# SOUNDS
mixer.init()
mixer.pre_init()
mixer.music.load("assets/sounds/music_0.wav")
mixer.music.play(-1)
mixer.music.set_volume(0.1)
atmosphere_sound = mixer.Sound("assets/sounds/horror_atmosphere_0.wav")
# atmosphere_sound.set_volume(0.75)
atmosphere_sound.play(-1)
ecto_collected_sound = mixer.Sound("assets/sounds/ecto_collected_1.wav")
ecto_hit_sound = mixer.Sound("assets/sounds/ecto_hit.mp3")
ecto_hit_sound.set_volume(0.50)
card_hovered_sound = mixer.Sound("assets/sounds/shop/card_hover_0.wav")
# card_hovered_sound.set_volume(0.75)
upgrade_bought_sound = mixer.Sound("assets/sounds/shop/upgrade_bought_1.wav")
cant_buy_sound = mixer.Sound("assets/sounds/shop/upgrade_bought_0.wav")
cant_buy_sound.set_volume(0.33)
out_of_ecto_sound = mixer.Sound("assets/sounds/error.wav")
out_of_ecto_sound.set_volume(0.50)
shooter_shoot_sound = mixer.Sound("assets/sounds/shooter_shoot_3.wav")
shooter_shoot_sound.set_volume(0.75)
spike_activate_sound = mixer.Sound("assets/sounds/spike_activate.wav")
spike_deactivate_sound = mixer.Sound("assets/sounds/spike_deactivate.wav")
spike_deactivate_sound.set_volume(0.1)

# CHANNELS
shop_channel = mixer.Channel(0)
collect_ecto_channel = mixer.Channel(1)
shooter_channels = [mixer.Channel(i) for i in range(2, 4)]

mouse.set_visible(False)
CURSOR_RECT = Rect(0, 0, 32, 32)
CURSOR = image.load("assets/sprites/player/cursor.png").convert_alpha()

TICK_RATE = 60

# FONTS
CB_12 = pg.font.Font("assets/UI/fonts/cambria-bold.ttf", 12)
CB_16 = pg.font.Font("assets/UI/fonts/cambria-bold.ttf", 16)
CB_24 = pg.font.Font("assets/UI/fonts/cambria-bold.ttf", 24)
CB_32 = pg.font.Font("assets/UI/fonts/cambria-bold.ttf", 32)
CB_50 = pygame.font.Font("assets/UI/fonts/cambria-bold.ttf", 50)

V_ZERO = Vector2(0, 0)
V_NORTH = Vector2(0, -1)
V_NORTH_EAST = Vector2(1, -1)
V_EAST = Vector2(1, 0)
V_SOUTH_EAST = Vector2(1, 1)
V_SOUTH = Vector2(0, 1)
V_SOUTH_WEST = Vector2(-1, 1)
V_WEST = Vector2(-1, 0)
V_NORTH_WEST = Vector2(-1, -1)
GRAVITY = Vector2(0, 5)

# DEBUG
DEBUG_INVINCIBLE = True
CUSTOM_SHOP_DEBUG = True


def create_line(x1, y1, x2, y2):
    return (x1, y1), (x2, y2)


def check_left_wall_collision(rect: Rect) -> bool:
    if rect.left <= 0:
        rect.x = 0
        return True
    return False


def check_right_wall_collision(rect: Rect) -> bool:
    if rect.right >= GAME_WIDTH:
        rect.x = GAME_WIDTH - rect.width
        return True
    return False


def check_ceil_collision(rect: Rect) -> bool:
    if rect.top <= 0:
        rect.y = 0
        return True
    return False


def check_floor_collision(rect: Rect) -> bool:
    if rect.bottom >= GAME_HEIGHT:
        rect.y = GAME_HEIGHT - rect.h
        return True
    return False


def check_wall_collision(rect: Rect) -> bool:
    collides: bool = False

    if check_right_wall_collision(rect):
        collides = True

    if check_left_wall_collision(rect):
        collides = True

    if check_floor_collision(rect):
        collides = True

    if check_ceil_collision(rect):
        collides = True

    return collides


def get_rand_point_for_rect(rect: Rect) -> Vector2:
    return Vector2(random.randint(0, GAME_WIDTH - rect.width), random.randint(0, GAME_HEIGHT - rect.height))


def generate_empty_grid(num_rows: int, num_cols: int) -> list[list]:
    grid = []
    for i in range(num_rows):
        row = [None for _ in range(num_cols)]
        grid.append(row)

    return grid


def generate_lined_text(text, max_length, text_font, color):
    lined_text = []
    start = 0
    curr = ""
    i = 0
    text_length = len(text)
    while i < text_length:
        if text[i] == "~":
            if curr != "":
                lined_text.append(text_font.render(curr.strip(), True, color))
                curr = ""
            j = i + 1
            start = j
            forced_line = ""
            while j < text_length and text[j] != "~":
                forced_line += text[j]
                j += 1

            lined_text.append(text_font.render(forced_line.strip(), True, color))
            start = j + 1
            i = start
            continue

        elif text[i] == " ":
            word = text[start:i]
            line = curr + " " + word
            text_size = text_font.size(line)
            if text_size[0] < max_length:
                curr = line
            else:
                lined_text.append(text_font.render(curr.strip(), True, color))
                curr = " " + word
            start = i + 1
        i += 1

    if curr != "":
        lined_text.append(text_font.render((curr.strip() + " " + text[start:text_length]).strip(), True, WHITE))
    return lined_text


def direction_to(pos: tuple, other_pos: tuple):
    dy = other_pos[1] - pos[1]
    dx = other_pos[0] - pos[0]

    direction = Vector2(dx, dy)

    if direction.length() != 0:
        direction = direction.normalize()
    return direction


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
    collected = False
    distance_traveled = 0
    max_range = 250
    damage = 5
    ecto_shoot_sound = mixer.Sound("assets/sounds/ecto_shoot_1.wav")
    ecto_shoot_sound.set_volume(0.5)

    def __init__(self, direction, spawn_pos, max_range=250):
        rect = Rect(0, 0, 16, 16)
        rect.center = spawn_pos
        self.max_range = max_range
        super().__init__(rect,
                         image.load("assets/sprites/player/ectoplasm.png").convert_alpha(),
                         direction,
                         10,
                         5,
                         True)
        self.damage = 5
        self.ecto_shoot_sound.play()

    def handle_hit(self):
        self.ecto_shoot_sound.stop()
        ecto_hit_sound.play()
        self.is_active = False

    def update(self):
        self.distance_traveled += self.velocity.magnitude()
        if self.distance_traveled >= self.max_range or check_wall_collision(self.rect):
            self.is_active = False
        if self.is_active:
            super().move()


class EctoShooter:
    num_ecto = 0
    max_num_ecto = 3
    ectos: list[Ectoplasm] = []
    spawn_pos: tuple = GAME_RECT.center
    guide_width = 16
    shooting: bool = False

    def set_spawn_pos(self, spawn_pos):
        self.spawn_pos = spawn_pos

    def get_shoot_direction(self):
        dx = CURSOR_RECT.centerx - self.spawn_pos[0]
        dy = CURSOR_RECT.centery - self.spawn_pos[1]

        direction = Vector2(dx, dy)
        if direction.length() != 0:
            direction = direction.normalize()
        return direction

    def create_ecto(self):
        return Ectoplasm(self.get_shoot_direction(), self.spawn_pos)

    def reset(self):
        pass

    def shoot(self, _dt):
        shoot_pressed = mouse.get_pressed()[0]
        self.shooting = shoot_pressed

        if self.num_ecto >= self.max_num_ecto:
            if not shoot_pressed:
                out_of_ecto_sound.play()
                self.shooting = False
            self.reset()
            return None

        if not shoot_pressed:
            ecto = self.create_ecto()
            self.num_ecto += 1
            self.shooting = False
            self.reset()
            return ecto

    def get_guide_end_point(self, start_point, direction):
        return (direction * Ectoplasm.max_range) + start_point

    def draw(self):
        if not self.shooting:
            return

        start_point = Vector2(self.spawn_pos)
        end_point = Vector2(CURSOR_RECT.center)
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y

        direction = Vector2(dx, dy)
        if direction.length() != 0:
            direction = direction.normalize()

        end_point = self.get_guide_end_point(start_point, direction)
        color = WHITE if self.num_ecto < self.max_num_ecto else Color(255, 0, 0)
        pg.draw.line(GAME_BACKGROUND, color, start_point, end_point, self.guide_width)


class ControlledRangeEctoShooter(EctoShooter):
    min_range = 50
    curr_range = min_range
    max_range = Ectoplasm.max_range
    time_held = 0

    def reset(self):
        self.time_held = 0
        self.curr_range = self.min_range

    def create_ecto(self):
        return Ectoplasm(self.get_shoot_direction(), self.spawn_pos, self.curr_range)

    def shoot(self, _dt):
        shoot_pressed = mouse.get_pressed()[0]
        self.shooting = shoot_pressed
        self.time_held += _dt
        updated_range = self.min_range + (self.time_held // 2)
        self.curr_range = updated_range if updated_range <= Ectoplasm.max_range else Ectoplasm.max_range
        return super().shoot(_dt)

    def get_guide_end_point(self, start_point, direction):
        return (direction * self.curr_range) + start_point


class Player:
    _instance = None
    rect = Rect(600, 400, 32, 32)
    sprite = image.load("assets/sprites/player/ghost_player.png").convert_alpha()
    velocity = V_ZERO
    ectos: list[Ectoplasm] = []
    speed = 5
    num_coins = 0
    num_ecto = 0
    max_num_ecto = 5
    phase_speed_modifier = 1.5
    phase_time = 0.33
    max_health = 20
    health = max_health
    shoot_direction: Vector2
    state = "MOVE"
    guide_width = 16
    out_of_ecto = False
    ecto_shooter = ControlledRangeEctoShooter()
    dt = 0

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
        if DEBUG_INVINCIBLE:
            return
        self.health -= damage

    def move(self):
        keys = pg.key.get_pressed()
        direction = self.__get_direction(keys)
        self.velocity = self.speed * direction
        self.rect = self.rect.move(self.velocity)

        check_wall_collision(self.rect)

        shoot_pressed = mouse.get_pressed()[0]
        if shoot_pressed:
            self.state = "SHOOT"

    def shoot(self):
        self.ecto_shooter.set_spawn_pos(self.rect.center)
        ecto = self.ecto_shooter.shoot(self.dt)

        if not self.ecto_shooter.shooting:
            if ecto:
                self.ectos.append(ecto)
            self.state = "MOVE"

    def update(self, _dt):
        self.dt = _dt
        match self.state:
            case "MOVE":
                self.move()
            case "SHOOT":
                self.shoot()

        uncollected_ectos = []
        for ecto in self.ectos:
            if ecto.rect.colliderect(self.rect) and not ecto.is_active:
                ecto.collected = True
                if not collect_ecto_channel.get_busy():
                    collect_ecto_channel.play(ecto_collected_sound)
                self.ecto_shooter.num_ecto -= 1

            ecto.update()

            if not ecto.collected:
                uncollected_ectos.append(ecto)
            self.ectos = uncollected_ectos

    def draw(self):
        for ecto in self.ectos:
            ecto.draw()
        self.ecto_shooter.draw()
        GAME_BACKGROUND.blit(self.sprite, (self.rect.x, self.rect.y))


class Essence:
    player = Player.get_instance()
    sprite = image.load("assets/sprites/player/essence.png").convert_alpha()
    rect: Rect = Rect(0, 0, 16, 16)
    value: int
    dt: int
    collected: bool = False
    direction: Vector2
    velocity: Vector2
    speed = 5
    max_y = GAME_HEIGHT
    uncollect_timer = 5000
    uncollect_time = 0
    blink_timer = 100
    blink_time = 0
    alpha = 255
    despawn = False

    def __init__(self, value: int, spawn_pos: tuple):
        self.max_y = random.randint(spawn_pos[1] + 8, spawn_pos[1] + 24)
        self.value = value
        self.rect.center = spawn_pos
        self.direction = V_NORTH.rotate(random.randint(-45, -15)) if random.randint(1, 2) == 1 \
            else V_NORTH.rotate(random.randint(15, 45))

    def give_value(self):
        self.player.num_coins += self.value

    def update(self, _dt):
        if self.despawn:
            return

        self.dt = _dt
        self.uncollect_time += self.dt

        if self.uncollect_time >= self.uncollect_timer:
            self.despawn = True
            return

        if self.uncollect_time >= self.uncollect_timer - 1000:
            self.blink_time += self.dt

            if self.blink_time >= self.blink_timer:
                self.alpha = 255 if self.alpha == 127 else 127
                self.blink_time = 0

        if self.rect.colliderect(self.player.rect):
            self.give_value()
            self.despawn = True
            return

        if self.speed == 0:
            return

        if self.rect.bottom > self.max_y or check_wall_collision(self.rect):
            self.speed = 0
            return

        self.velocity = self.direction * self.speed
        self.direction += (GRAVITY * (self.dt / 1500))
        self.rect = self.rect.move(self.velocity)
        if self.player.rect.colliderect(self.rect):
            self.collected = True
            self.give_value()

    def draw(self):
        if self.despawn:
            return
        self.sprite.set_alpha(self.alpha)
        SCREEN.blit(self.sprite, self.rect)


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
    dead = False
    target_point: Vector2
    telegraph_text = CB_24.render("!", True, (255, 0, 0))
    telegraph_text_rect = telegraph_text.get_rect()

    def __init__(self, w, h, sprite: Surface, speed: int, difficulty: int, health: int, attack_rate: int,
                 outside_spawn: bool, telegraph_time: int = 400):
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
        self.target_point = self.get_target_point()

    def get_target_point(self):
        return Vector2(self.player.rect.center)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.dead = True

    def get_desired_direction(self):
        return direction_to(self.rect.center, self.player.rect.center)

    def steer(self, enemies: list, index):
        desired_direction = self.get_desired_direction()
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

        steer_map: list[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        best_direction_index = 0
        for i in range(8):
            interest = interest_weights[i] - danger_weights[i]
            steer_map[i] = interest
            if steer_map[best_direction_index] < interest:
                best_direction_index = i
        desired_velocity = self.steer_directions[best_direction_index] + desired_direction
        if desired_velocity.length() != 0:
            desired_velocity = desired_velocity.normalize() * self.speed
        self.velocity += desired_velocity

    def get_direction_to_player(self):
        dy = self.player.rect.centery - self.rect.centery
        dx = self.player.rect.centerx - self.rect.centerx

        direction = Vector2(dx, dy)

        if direction.length() != 0:
            direction = direction.normalize()
        return direction

    def get_distance_to_player(self):
        return math.sqrt((abs(self.player.rect.centery - self.rect.centery) ** 2) +
                         (abs(self.player.rect.centerx - self.rect.centerx) ** 2))

    def move(self):
        if self.velocity.length() != 0:
            self.velocity = self.velocity.normalize() * self.speed
        self.rect = self.rect.move(self.velocity)
        check_wall_collision(self.rect)

    def attack(self):
        pass

    def telegraph(self):
        self.telegraph_timer += self.dt
        self.telegraph_text_rect.bottom = self.rect.top - 2
        self.telegraph_text_rect.centerx = self.rect.centerx
        if self.telegraph_timer >= self.telegraph_time:
            self.telegraph_timer = 0
            self.state = "ATTACK"

    def idle(self):
        pass

    def update(self, _dt):
        self.dt = _dt
        if self.dead:
            return

        match self.state:
            case "MOVE":
                self.move()
            case "ATTACK":
                self.attack()
            case "TELEGRAPH":
                self.telegraph()
            case "IDLE":
                self.idle()

        for ecto in self.player.ectos:
            if ecto.rect.colliderect(self.rect) and ecto.is_active:
                ecto.handle_hit()
                self.take_damage(ecto.damage)

    def draw(self):
        if self.dead:
            return

        GAME_BACKGROUND.blit(self.sprite, self.rect)

        if self.state == "TELEGRAPH":
            GAME_BACKGROUND.blit(self.telegraph_text, self.telegraph_text_rect)


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
        w = 24
        h = 24
        super().__init__(w, h, Surface((w, h)), 2, 2, 5, 2000, True,
                         400)
        self.sprite = image.load("assets/sprites/enemy/dasher_0.png").convert_alpha()

    def move(self):
        self.speed = self.base_speed
        self.last_attack += self.dt
        self.target_point = Vector2(self.player.rect.center)
        if self.last_attack >= self.attack_rate and self.get_distance_to_player() <= self.dash_range:
            self.dash_direction = direction_to(self.rect.center, self.player.rect.center)
            self.telegraph_text_rect.bottom = self.rect.top
            self.telegraph_text_rect.centerx = self.rect.centerx
            self.last_attack = 0
            self.state = "TELEGRAPH"

        super().move()

    def attack(self):
        self.speed = self.dash_speed
        self.velocity = self.dash_direction * self.speed

        super().move()
        self.dash_distance += self.velocity.magnitude()

        if not self.delt_damage and self.rect.colliderect(self.player.rect):
            self.delt_damage = True
            self.player.take_damage(1)

        if self.dash_distance >= self.max_dash_distance:
            self.delt_damage = False
            self.dash_distance = 0
            self.state = "MOVE"


class EnemyProjectile(Projectile):
    player = Player.get_instance()

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

    def draw(self):
        if self.is_active:
            super().draw()


class Shooter(Enemy):
    projectiles: list[EnemyProjectile] = []
    curr_shooter_channel = 0
    idle_timer = 0
    idle_time = 0
    idle_chance = 10

    def __init__(self):
        w = 24
        h = 24
        super().__init__(w, h, Surface((w, h)), 2, 3, 5, 4000, True)
        self.sprite = image.load("assets/sprites/enemy/skull_0.png").convert_alpha()

    def move(self):
        if self.get_distance_to_player() <= 250:
            self.velocity -= self.get_direction_to_player() * (self.speed * 2)

        super().move()
        self.last_attack += self.dt

        if self.last_attack >= self.attack_rate:
            self.last_attack = 0
            self.state = "ATTACK"

    def attack(self):
        self.projectiles.append(EnemyProjectile(self.rect.center, self.get_direction_to_player()))

        channel = shooter_channels[self.curr_shooter_channel]
        if not channel.get_busy():
            channel.play(shooter_shoot_sound)

        Shooter.curr_shooter_channel += 1
        if Shooter.curr_shooter_channel >= len(shooter_channels):
            Shooter.curr_shooter_channel = 0

        idle_num = random.randint(1, 5)
        if idle_num == self.idle_chance:
            self.idle_timer = 3000
            self.state = "IDLE"

            return
        self.state = "MOVE"

    def idle(self):
        self.idle_time += self.dt
        if self.idle_time >= self.idle_timer:
            self.idle_time = 0
            self.state = "MOVE"

    def update(self, _dt):
        projectiles_to_keep = []
        for s in self.projectiles:
            s.update()
            if s.is_active:
                projectiles_to_keep.append(s)

        self.projectiles = projectiles_to_keep
        super().update(_dt)

    def draw(self):
        if self.dead:
            return

        for p in self.projectiles:
            p.draw()
        super().draw()


class Beamer(Enemy):
    beam: tuple
    beam_length = 110
    beam_angle = 0
    beam_width = 8
    beam_start = V_ZERO
    beam_end = V_ZERO
    rotate_speed = 2.5
    base_speed = 3
    attack_speed = 2

    def __init__(self):
        super().__init__(24, 24, Surface((20, 20)), self.base_speed, 1, 5, 5000, True)
        self.sprite.fill("purple")
        self.beam_start = self.rect.center
        self.beam_end = self.beam_start + (V_NORTH.rotate(self.beam_angle) * self.beam_length)

    def move(self):
        super().move()
        self.last_attack += self.dt

        if self.last_attack >= self.attack_rate:
            self.last_attack = 0
            self.beam_start = self.rect.center
            self.beam_end = self.beam_start + (V_NORTH.rotate(self.beam_angle) * self.beam_length)
            self.state = "ATTACK"

    def attack(self):
        self.speed = self.attack_speed
        self.beam_start = Vector2(self.rect.center)
        self.beam_end = self.beam_start + (V_NORTH.rotate(self.beam_angle) * self.beam_length)
        self.beam_angle += self.rotate_speed

        super().move()

        if self.beam_angle > 360:
            self.state = "MOVE"
            self.speed = self.base_speed
            self.beam_angle = 0

    def draw(self):
        if self.dead:
            return

        if self.state == "ATTACK":
            pg.draw.line(GAME_BACKGROUND, WHITE, self.beam_start, self.beam_end, self.beam_width)

        super().draw()


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
        rand_int = random.randint(1, 3)
        match rand_int:
            case 1:
                return Shooter()
            case 2:
                return Dasher()
            case 3:
                return Beamer()


class EnemyManager:
    _instance = None
    unspawned_enemies: list[Enemy] = []
    spawned_enemies: list[Enemy] = []
    dead_projectiles: list[EnemyProjectile] = []
    essences: list[Essence] = []
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
                return 6
            case 2:
                return 12
            case 3:
                return 18
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
        self.dead_projectiles = []
        self.wave_complete = False

        while self.difficulty > 0:
            enemy = EnemyFactory.create_enemy()
            self.unspawned_enemies.append(enemy)
            self.difficulty -= enemy.difficulty

    def update(self, _dt: int):
        all_dead = True
        for i in range(len(self.spawned_enemies)):
            enemy = self.spawned_enemies[i]
            if enemy.dead:
                continue

            enemy.steer(self.spawned_enemies, i)
            enemy.update(_dt)

            if not enemy.dead:
                all_dead = False
            else:
                for n in range(random.randint(1, 5)):
                    self.essences.append(Essence(1, enemy.rect.center))

                if enemy.__class__ == Shooter:
                    self.dead_projectiles = self.dead_projectiles + enemy.projectiles

        for p in self.dead_projectiles:
            p.update()

        self.last_spawn += _dt

        for ess in self.essences:
            ess.update(_dt)

        len_unspawned = len(self.unspawned_enemies)

        if self.last_spawn >= self.spawn_rate and len_unspawned > 0:
            self.spawned_enemies.append(self.unspawned_enemies.pop(0))
            self.last_spawn = 0

        if len_unspawned <= 0 and all_dead:
            self.wave_complete = True

    def draw(self):
        for ess in self.essences:
            ess.draw()

        for p in self.dead_projectiles:
            p.draw()

        for enemy in self.spawned_enemies:
            enemy.draw()


class Hazard:
    player: Player = Player.get_instance()
    rect: Rect
    sprite: Surface
    state: str = "ACTIVE"
    active_timer = 0
    active_time = 0
    inactive_timer = 0
    inactive_time = 0
    dt = 0

    def __init__(self, x, y, sprite: Surface):
        self.rect = Rect(x, y, 40, 40)
        self.sprite = sprite

    def active(self):
        pass

    def inactive(self):
        pass

    def update(self, _dt):
        self.dt = _dt
        match self.state:
            case "ACTIVE":
                self.active()
            case "INACTIVE":
                self.inactive()

    def draw(self):
        GAME_BACKGROUND.blit(self.sprite, (self.rect.x, self.rect.y))


class Spike(Hazard):
    active_sprite = image.load("assets/sprites/hazards/spikes.png")
    inactive_sprite = image.load("assets/sprites/hazards/inactive_spikes.png")

    def __init__(self, x, y):
        super().__init__(x, y, self.active_sprite)
        self.active_timer = 5000
        self.inactive_timer = 5000

    def active(self):
        if self.rect.colliderect(self.player.rect):
            self.player.take_damage(1)
            self.sprite = self.inactive_sprite
            spike_deactivate_sound.play()
            self.state = "INACTIVE"
        self.active_time += self.dt

        if self.active_time >= self.active_timer:
            self.active_time = 0
            self.sprite = self.inactive_sprite
            spike_deactivate_sound.play()
            self.state = "INACTIVE"

    def inactive(self):
        self.inactive_time += self.dt

        if self.inactive_time >= self.inactive_timer:
            self.sprite = self.active_sprite
            self.inactive_time = 0
            spike_activate_sound.play()
            self.state = "ACTIVE"


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
        half_row = self.grid_size[0] // 2
        half_col = self.grid_size[1] // 2
        for row_ind in range(1, self.grid_size[0]):
            for col_ind in range(1, self.grid_size[1]):
                if ((row_ind == half_row or row_ind == half_row + 1) and
                        (col_ind == half_col or col_ind == half_col + 1)):
                    continue
                rand_num = random.randint(1, 64)
                if rand_num == 64:
                    hazard = Spike(col_ind * 40, row_ind * 40)
                    self.hazards.append(hazard)

    def update(self, _dt):
        for h in self.hazards:
            h.update(_dt)

    def draw(self):
        for h in self.hazards:
            h.draw()


class Upgrade:
    player = Player.get_instance()
    cost: int
    rect: Rect
    card: Surface
    sold_card = image.load("assets/shop/sold_card.png").convert_alpha()
    info_card = image.load("assets/shop/empty_card.png")
    curr_card: Surface
    highlight = Surface((200, 200))
    highlight_rect: Rect
    highlight.fill("white")
    clicked = False
    bought = False
    hovered = False
    hover_sound_played = False
    hover_offset = 10
    cant_buy_sound_played = False
    upgrade_id: int = 0
    info_text: list[Surface]
    upgrade_text: list[Surface]
    info_font = CB_16
    upgrade_font = CB_24
    text_offset = tuple((20, 20))
    cost_text: Surface
    essence_img = image.load("assets/sprites/player/essence.png").convert_alpha()

    def __init__(self, cost: int, info_text: str, upgrade_text: str):
        self.rect = Rect(0, 0, 200, 200)
        self.highlight_rect = Rect(0, 0, 200, 200)
        self.card = pg.image.load("assets/shop/empty_card_1.png")
        self.curr_card = self.card
        self.essence_img = pg.transform.scale(self.essence_img, (32, 32))
        self.cost = cost
        self.upgrade_id = Upgrade.upgrade_id
        self.info_text = generate_lined_text(info_text, 160, self.info_font, WHITE)
        self.upgrade_text = generate_lined_text(upgrade_text, 160, self.upgrade_font, WHITE)
        self.cost_text = CB_32.render(f"{self.cost}", True, DARK_BLUE)

        Upgrade.upgrade_id += 1

    def update_info_text(self, info_text):
        self.info_text = generate_lined_text(info_text, 160, self.info_font, WHITE)

    def set_shop_position(self, position: tuple):
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.highlight_rect.x = position[0]
        self.highlight_rect.y = position[1]

    def apply_upgrade(self):
        pass

    def update(self):
        pressed = mouse.get_pressed()[0]
        self.hovered = self.highlight_rect.collidepoint(mouse.get_pos())

        if self.hovered:
            if not self.hover_sound_played:
                card_hovered_sound.play()
                self.hover_sound_played = True
            self.curr_card = self.info_card if not self.bought else self.sold_card
            self.rect.x = self.highlight_rect.x + self.hover_offset
            self.rect.y = self.highlight_rect.y - self.hover_offset
        else:
            self.curr_card = self.card if not self.bought else self.sold_card
            self.hover_sound_played = False
            self.clicked = False
            self.rect.x = self.highlight_rect.x
            self.rect.y = self.highlight_rect.y
            return

        if pressed:
            self.clicked = True
            time.wait(120)

        if self.clicked and not pressed:
            if self.bought:
                card_hovered_sound.stop()
                cant_buy_sound.play()
                self.clicked = False
                return

            if self.player.num_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.bought = True
                self.apply_upgrade()
                self.curr_card = self.sold_card
                card_hovered_sound.stop()
                upgrade_bought_sound.play()
            else:
                card_hovered_sound.stop()
                cant_buy_sound.play()
            self.clicked = False

    def draw(self):
        if self.hovered:
            GAME_BACKGROUND.blit(self.highlight, self.highlight_rect)

        GAME_BACKGROUND.blit(self.curr_card, self.rect)

        if not self.bought:
            if self.hovered:
                for i in range(len(self.info_text)):
                    line = self.info_text[i]
                    GAME_BACKGROUND.blit(line,
                                         (self.rect.x + self.text_offset[0],
                                          self.rect.y + (i * 16) + self.text_offset[1]))
            else:
                for i in range(len(self.upgrade_text)):
                    line = self.upgrade_text[i]
                    line_rect = line.get_rect()
                    GAME_BACKGROUND.blit(line, (
                        self.rect.centerx - (line_rect.w // 2), self.rect.y + (i * 24) + self.text_offset[1]))
                GAME_BACKGROUND.blit(self.essence_img,
                                     (self.rect.centerx - 36, self.rect.bottom - self.text_offset[1] - 32))
                GAME_BACKGROUND.blit(self.cost_text,
                                     (self.rect.centerx + 4, self.rect.bottom - self.text_offset[1] - 32))


# UPGRADES BELOW THIS LINE
class MaxHealthUpgrade(Upgrade):

    def __init__(self):
        info_text = f"Increase your maximum health by  1 ~ ~ ~MAXIMUM HEALTH:~ ~{self.player.max_health} -> {self.player.max_health + 1}~"
        upgrade_text = "Max Health ~+1~"
        super().__init__(5, info_text, upgrade_text)

    def apply_upgrade(self):
        self.player.max_health += 1
        self.player.health += 1
        self.update_info_text(
            f"Increase your maximum health by  1 ~ ~ ~MAXIMUM HEALTH:~ ~{self.player.max_health} -> {self.player.max_health + 1}~")


class NumEctoUpgrade(Upgrade):
    def __init__(self):
        info_text = f"Increase how many Ectoplasm you can shoot before you run out ~ ~ ~ECTOPLASM:~ ~{self.player.ecto_shooter.max_num_ecto} -> {self.player.ecto_shooter.max_num_ecto + 1}~"
        upgrade_text = "Ectoplasm ~+1~"
        super().__init__(5, info_text, upgrade_text)

    def apply_upgrade(self):
        self.player.ecto_shooter.max_num_ecto += 1
        EctoShooter.max_num_ecto += 1
        self.update_info_text(
            f"Increase how many Ectoplasm you can shoot before you run out ~ ~ ~ECTOPLASM RANGE:~ ~{self.player.ecto_shooter.max_num_ecto} -> {self.player.ecto_shooter.max_num_ecto + 1}~")


class EctoRangeUpgrade(Upgrade):
    def __init__(self):
        info_text = f"Increase how far you Ectoplasm travels by 10 percent ~ ~ ~ECTOPLASM RANGE:~ ~{Ectoplasm.max_range} -> {Ectoplasm.max_range * 1.1}~"
        upgrade_text = "Ectoplasm ~+10%~"
        super().__init__(5, info_text, upgrade_text)

    def apply_upgrade(self):
        Ectoplasm.max_range *= 1.1
        self.update_info_text(
            f"Increase how far you Ectoplasm travels by 10 percent ~ ~ ~ECTOPLASM RANGE:~ ~{Ectoplasm.max_range} -> {Ectoplasm.max_range * 1.1}~")


class RestoreHealthUpgrade(Upgrade):
    def __init__(self):
        info_text = f"Restore your SOUL to your MAXIMUM SOUL ~ ~ ~SOUL:~ ~{self.player.health} -> {self.player.max_health}~"
        upgrade_text = "Soul ~Restoration~"
        super().__init__(10, info_text, upgrade_text)

    def apply_upgrade(self):
        self.player.health = self.player.max_health
        self.update_info_text(
            f"Restore your health to your maximum health ~ ~ ~HEALTH:~ ~{self.player.health} -> {self.player.max_health}~")


class PlayerSpeedUpgrade(Upgrade):
    def __init__(self):
        info_text = f"Increase your movement speed by 1 ~ ~ ~SPEED:~ ~{self.player.speed} -> {self.player.speed + 1}~"
        upgrade_text = "Swift ~Spirit~"
        super().__init__(7, info_text, upgrade_text)

    def apply_upgrade(self):
        self.player.speed += 1
        self.update_info_text(
            f"Increase your movement speed by 1 ~ ~ ~SPEED:~ ~{self.player.speed} -> {self.player.speed + 1}~")


class EctoDamageUpgrade(Upgrade):
    def __init__(self):
        info_text = f"Increase the damage delt by Ectoplasm by 1 ~ ~ ~ECTOPLASM DAMAGE:~ ~{Ectoplasm.damage} -> {Ectoplasm.damage + 1}~"
        upgrade_text = "Injurious ~Ectoplasm~"
        super().__init__(5, info_text, upgrade_text)

    def apply_upgrade(self):
        Ectoplasm.damage += 1
        self.update_info_text(
            f"Increase the damage delt by Ectoplasm by 1 ~ ~ ~ECTOPLASM DAMAGE:~ ~{Ectoplasm.damage} -> {Ectoplasm.damage + 1}~")


class ControlRangeUpgrade(Upgrade):
    def __init__(self):
        info_text = "Control the distance of how far your Ectoplasm travels by holding down the mouse button before you shoot"
        upgrade_text = "Spectral ~Concentration~"
        super().__init__(20, info_text, upgrade_text)

    def apply_upgrade(self):
        self.player.ecto_shooter = ControlledRangeEctoShooter()
        self.update_info_text(
            "Control the distance of how far your Ectoplasm travels by holding down the mouse button before you shoot")


class Shop:
    _instance = None
    rect: Rect
    continue_text = CB_24.render("Press [SPACE] to Continue", True, WHITE)
    continue_text_rect = continue_text.get_rect()
    continue_text_rect.centerx = GAME_RECT.centerx
    continue_text_rect.bottom = GAME_HEIGHT - 20

    all_upgrades: list[Upgrade] = [
        MaxHealthUpgrade(),
        NumEctoUpgrade(),
        RestoreHealthUpgrade(),
        EctoRangeUpgrade(),
        PlayerSpeedUpgrade(),
        EctoDamageUpgrade(),
        ControlRangeUpgrade()
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
        if CUSTOM_SHOP_DEBUG:
            self.shop_upgrades = [
                self.all_upgrades[0],
                self.all_upgrades[1],
                self.all_upgrades[6]
            ]
            for i in range(3):
                self.shop_upgrades[i].set_shop_position(self.positions[i])
            return

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

        SCREEN.blit(self.continue_text, self.continue_text_rect)


class GameUI:
    font = pygame.font.Font("assets/UI/fonts/cambria-bold.ttf", 50)
    timer = 0
    timer_active = False
    dt = 0

    # Load ectoplasm image
    ectoplasm_image = pygame.image.load('assets/sprites/player/ectoplasm.png').convert_alpha()
    ectoplasm_image = pygame.transform.scale(ectoplasm_image, (50, 50))
    essence_img = image.load("assets/sprites/player/essence.png").convert_alpha()
    essence_img = pg.transform.scale(essence_img, (50, 50))
    healthbar_boarder = image.load("assets/UI/healthbar.png").convert_alpha()

    def __init__(self):
        self.player = Player.get_instance()

    def draw_health_bar(self, surface, x, y):
        max_health = self.player.max_health
        bar_width = 200
        bar_height = 50
        boarder_offset = 19

        # Health bar background
        pygame.draw.rect(surface, HEALTHBAR_LOWER_COLOR, (x, y, bar_width, bar_height))

        # Health bar foreground (based on current health)
        current_health_width = (self.player.health / max_health) * bar_width
        pygame.draw.rect(surface, HEALTHBAR_HIGHER_COLOR, (x, y, current_health_width, bar_height))
        SCREEN.blit(self.healthbar_boarder, (x - boarder_offset, y))

    def draw_coin_counter(self, surface, x, y):
        text = CB_50.render(f"{self.player.num_coins}", True, WHITE)
        surface.blit(self.essence_img, (x - 55, y))
        surface.blit(text, (x, y))

    def draw_ectoplasm(self, surface, x, y):
        text = CB_50.render(
            f"{self.player.ecto_shooter.max_num_ecto - self.player.ecto_shooter.num_ecto}/{self.player.ecto_shooter.max_num_ecto}",
            True, WHITE
        )
        text_rect = text.get_rect()
        text_rect.x = x + self.ectoplasm_image.get_width() + 20
        text_rect.y = y
        surface.blit(self.ectoplasm_image, (x, y))
        surface.blit(text, text_rect)

    def draw_timer(self, _dt, y):
        if not self.timer_active:
            return

        self.timer += _dt
        hours = self.timer // 3600000
        hours_milli = hours * 360000
        mins = (self.timer - hours_milli) // 60000
        mins_milli = mins * 60000
        secs = (self.timer - hours_milli - mins_milli) // 1000

        sec_text = str(secs) if secs >= 10 else "0" + str(secs)
        min_text = str(mins) if mins >= 10 else "0" + str(mins)
        hour_text = str(hours) if hours >= 10 else "0" + str(hours)

        text = CB_50.render(f"{hour_text}:{min_text}:{sec_text}", True, "White")
        text_rect = text.get_rect()
        text_rect.x = GAME_RECT.right - text_rect.w - 20
        text_rect.y = y

        SCREEN.blit(text, text_rect)

    def update(self, _dt):
        self.dt = _dt

    def draw(self):
        SCREEN.fill(SCREEN_COLOR)
        # Draw the UI elements in a horizontal line
        y_position = GAME_HEIGHT + 15  # Keep the same Y position for all elements

        # Starting X positions for the elements
        x_health_bar = 50
        x_coin_counter = x_health_bar + 300  # Adjust spacing after health bar
        x_ectoplasm = x_coin_counter + 100  # Adjust spacing after coin counter

        # Draw the health bar
        self.draw_health_bar(SCREEN, x_health_bar, y_position)

        # Draw the coin counter
        self.draw_coin_counter(SCREEN, x_coin_counter, y_position)

        # Draw the ectoplasm image
        self.draw_ectoplasm(SCREEN, x_ectoplasm, y_position)

        self.draw_timer(self.dt, y_position)


class Game:
    _instance = None
    player: Player
    enemy_manager: EnemyManager
    hazard_manager: HazardManager
    shop: Shop
    curr_wave = 1
    MAX_WAVES = 3
    clock = time.Clock()
    state = "HOME"
    prev_state = "WAVE"
    game_ui = GameUI()
    info_screen = image.load("assets/UI/info_screen.png").convert()
    dt = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def load_entities(self):
        self.player = Player.get_instance()
        self.enemy_manager = EnemyManager.get_instance()
        self.shop = Shop().get_instance()
        self.enemy_manager.load_enemies(self.curr_wave)
        self.game_ui = GameUI()
        self.hazard_manager = HazardManager.get_instance()
        self.hazard_manager.load_hazards()

    def restart_game(self):
        # TODO IMPLEMENT PROPERLY
        self.curr_wave = 1
        self.enemy_manager.load_enemies(self.curr_wave)
        self.player.rect.center = GAME_RECT.center
        self.state = "WAVE"

    @staticmethod
    def update_cursor():
        CURSOR_RECT.topleft = mouse.get_pos()

    @staticmethod
    def draw_cursor():
        SCREEN.blit(CURSOR, (CURSOR_RECT.x, CURSOR_RECT.y))

    def update_wave(self):
        keys = pg.key.get_pressed()
        if keys[K_i]:
            self.state = "INFO"
            self.prev_state = "WAVE"
        self.game_ui.timer_active = True
        self.player.update(self.dt)
        self.enemy_manager.update(self.dt)
        self.hazard_manager.update(self.dt)

        if self.player.health <= 0:
            self.state = "GAME_OVER"

        if self.enemy_manager.wave_complete:
            self.player.rect.centerx = GAME_RECT.centerx
            self.player.rect.centery = GAME_RECT.centery
            self.player.ecto_shooter.num_ecto = 0
            self.player.ectos = []
            self.enemy_manager.dead_projectiles = []

            if self.curr_wave < self.MAX_WAVES:
                self.shop.set_upgrades()
                self.state = "SHOP"
            else:
                self.state = "GAME_OVER"

    def update_shop(self):
        keys = pg.key.get_pressed()
        if keys[K_i]:
            self.state = "INFO"
            self.prev_state = "SHOP"

        if keys[K_SPACE]:
            self.shop.close()
            self.curr_wave += 1
            self.enemy_manager.load_enemies(self.curr_wave)
            self.enemy_manager.essences = []
            self.enemy_manager.dead_projectiles = []
            self.hazard_manager.load_hazards()
            self.state = "WAVE"

        self.shop.update()

    def update_info(self):
        keys = pg.key.get_pressed()
        self.game_ui.timer_active = False
        if keys[K_e]:
            self.state = self.prev_state

    def update_home(self):
        self.state = "INFO"

    def update_game_over(self):
        keys = pg.key.get_pressed()
        if keys[K_SPACE]:
            self.restart_game()

    def draw_home(self):
        pass

    def draw_wave(self):
        SCREEN.blit(GAME_BACKGROUND, (0, 0))
        GAME_BACKGROUND.fill(BG_COLOR)
        self.hazard_manager.draw()
        self.player.draw()
        self.enemy_manager.draw()

    def draw_shop(self):
        SCREEN.blit(GAME_BACKGROUND, (0, 0))
        GAME_BACKGROUND.fill(BG_COLOR)
        self.shop.draw()

    def draw_info(self):
        SCREEN.blit(self.info_screen, (0, 0))

    def draw_game_over(self):
        if self.player.health > 0:
            SCREEN.blit(image.load("assets/UI/congratulations.png"), V_ZERO)
        else:
            SCREEN.blit(image.load("assets/UI/you_died.png"), V_ZERO)

    def update(self, _dt):
        self.dt = _dt
        match self.state:
            case "HOME":
                self.update_home()
            case "WAVE":
                self.update_wave()
            case "SHOP":
                self.update_shop()
            case "INFO":
                self.update_info()
            case "GAME_OVER":
                self.update_game_over()

        self.game_ui.update(self.dt)
        self.update_cursor()

    def draw(self):
        self.game_ui.draw()

        match self.state:
            case "HOME":
                self.draw_home()
            case "WAVE":
                self.draw_wave()
            case "SHOP":
                self.draw_shop()
            case "INFO":
                self.draw_info()
            case "GAME_OVER":
                self.draw_game_over()

        self.draw_cursor()
        display.flip()


if __name__ == "__main__":
    game = Game.get_instance()
    game.load_entities()
    clock = time.Clock()

    while True:
        for e in pg.event.get():
            if e.type == QUIT:
                pg.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    pg.quit()
                    sys.exit()

        game.update(clock.get_time())
        game.draw()

        clock.tick(60)
