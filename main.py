import math

import pygame as pg
from pygame import Vector2, Rect, Surface, time, mouse, image, display
import random

pg.init()
display.set_caption("Ecto-Blast-Em")
mouse.set_visible(False)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
SCREEN = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
SCREEN.fill("Red")


class Ectoplasm:
    rect: Rect = None
    sprite: Surface = None
    direction: Vector2 = None
    speed = 10
    damage = 5
    velocity: Vector2 = None
    is_active = True
    is_collected = False
    distance_traveled = 0
    max_range = 250

    def __init__(self, x, y, direction):
        self.rect = Rect(x + 8, y + 8, 16, 16)
        self.sprite = image.load("assets/sprites/player/ectoplasm.png").convert_alpha()
        self.direction = direction

    def handle_enemy_hit(self):
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
            self.velocity = self.direction * self.speed
            self.rect = self.rect.move(self.velocity)

            if self.distance_traveled >= self.max_range:
                self.is_active = False

    def draw(self, background: Surface):
        background.blit(self.sprite, Vector2(self.rect.x, self.rect.y))


class Player:
    _instance = None
    rect = Rect(600, 400, 32, 32)
    sprite = image.load("assets/sprites/player/ghost_player.png").convert_alpha()
    velocity = Vector2(0, 0)
    ectos: list[Ectoplasm] = []
    speed = 15
    num_coins = 15
    num_ecto = 0
    max_num_ecto = 5
    phase_speed_modifier = 1.5
    phase_time = 0.33
    max_health = 10
    health = 10
    shoot_pressed: bool = False
    shoot_direction: Vector2 = Vector2(0, -1)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def update(self, last_tick: int):
        # MOVE THE PLAYER
        keys = pg.key.get_pressed()

        x_strength = int(keys[pg.K_RIGHT]) - int(keys[pg.K_LEFT])
        y_strength = int(keys[pg.K_DOWN]) - int(keys[pg.K_UP])

        direction = Vector2(x_strength, y_strength)
        if x_strength != 0 or y_strength != 0:
            direction = direction.normalize()
            self.shoot_direction = direction

        desired_velocity: Vector2 = self.speed * direction
        steering_force = desired_velocity - self.velocity * 1.5
        self.velocity += steering_force * (last_tick / 1000)

        # SHOOT ECTOPLASM
        c_pressed = keys[pg.K_c]
        if c_pressed and len(self.ectos) != self.max_num_ecto:
            self.shoot_pressed = True

        if not c_pressed and self.shoot_pressed and self.num_ecto < self.max_num_ecto:
            ecto = Ectoplasm(self.rect.x, self.rect.y, self.shoot_direction)
            self.ectos.append(ecto)
            self.shoot_pressed = False
            self.num_ecto += 1

        uncollected_ectos = []
        for ecto in self.ectos:
            if ecto.rect.colliderect(self.rect) and not ecto.is_active:
                ecto.is_collected = True
                self.num_ecto -= 1

            ecto.update()

            if not ecto.is_collected:
                uncollected_ectos.append(ecto)
            self.ectos = uncollected_ectos
        self.rect = self.rect.move(self.velocity)

    def draw(self, background: Surface):
        for ecto in self.ectos:
            ecto.draw(background)
        background.blit(self.sprite, (self.rect.x, self.rect.y))


class Enemy:
    game = None
    player: Player = None
    rect: Rect = Rect(0, 0, 50, 50)
    sprite: Surface = Surface((50, 50))
    difficulty = 2
    health = 0
    speed = 1.5
    velocity: Vector2 = Vector2(0, 0)
    is_environmental = False
    color = None
    steer_directions = [Vector2(0, -1),
                        Vector2(1, -1),
                        Vector2(1, 0),
                        Vector2(1, 1),
                        Vector2(0, 1),
                        Vector2(-1, 1),
                        Vector2(-1, 0),
                        Vector2(-1, -1)]

    def __init__(self, width, height, difficulty, health, start_pos: Vector2):
        self.player = Player.get_instance()
        self.rect = Rect(start_pos.x, start_pos.y, width, height)
        self.difficulty = difficulty
        self.health = health
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

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

        steer_rays = [
            ((mt[0], mt[1]), (mt[0], mt[1] - 10)),
            ((tr[0], tr[1]), (tr[0] + 5, tr[1] - 5)),
            ((mr[0], mr[1]), (mr[0] + 10, mr[1])),
            ((br[0], br[1]), (br[0] + 5, br[1] + 5)),
            ((mb[0], mb[1]), (mb[0], mb[1] + 10)),
            ((bl[0], bl[1]), (bl[0] - 5, bl[1] + 5)),
            ((ml[0], ml[1]), (ml[0] - 10, ml[1])),
            ((tl[0], tl[1]), (tl[0] - 5, tl[1] - 5)),
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
            context = interest_weights[i] - danger_weights[i]
            steer_map[i] = context
            if steer_map[best_direction_index] < context:
                best_direction_index = i
        desired_velocity = self.steer_directions[best_direction_index] * self.speed
        steering_force = desired_velocity - self.velocity * (random.randint(1, 10) / 10)
        self.velocity += steering_force

    def get_desired_direction(self):
        slope_y = self.player.rect.centery - self.rect.centery
        slope_x = self.player.rect.centerx - self.rect.centerx

        direction = Vector2(slope_x, slope_y)

        if slope_y != 0 or slope_x != 0:
            direction = direction.normalize()

        return direction

    def update(self):
        self.velocity = self.velocity.normalize() * self.speed
        self.rect = self.rect.move(self.velocity)
        for e in self.player.ectos:
            if e.rect.colliderect(self.rect) and e.is_active:
                e.handle_enemy_hit()
                self.take_damage(e.damage)

    def draw(self, background: Surface):
        self.sprite.fill(self.color)
        background.blit(self.sprite, (self.rect.x, self.rect.y))


class EnemyFactory:
    _instance = None
    enemy_types = []
    times_called = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def create_enemy(cls) -> Enemy:
        e = Enemy(50, 50, 2, 5, Vector2(50, 50))
        cls.times_called += 1
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

    def load_enemies_for_wave(self, curr_wave: int):
        self.spawn_rate = self.__get_spawn_rate(curr_wave)
        self.difficulty = self.__get_difficulty(curr_wave)
        self.last_spawn = 0
        self.wave_complete = False
        self.__create_enemies()

    def __create_enemies(self):
        while self.difficulty > 0:
            e = EnemyFactory.create_enemy()
            if e.is_environmental:
                self.spawned_enemies.append(e)
            else:
                self.unspawned_enemies.append(e)
            self.difficulty -= e.difficulty

    def update(self, last_tick: int):
        enemies_to_keep: list[Enemy] = []

        for i in range(len(self.spawned_enemies)):
            e = self.spawned_enemies[i]
            desired_direction = e.get_desired_direction()
            e.steer(desired_direction, self.spawned_enemies, i)
            e.update()
            if e.health > 0:
                enemies_to_keep.append(e)

        self.spawned_enemies = enemies_to_keep
        self.last_spawn += last_tick

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


# ALL IMPLEMENT NEW UPGRADES BELOW THIS LINE
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
        self.enemy_manager.load_enemies_for_wave(self.curr_wave)
        self.player.rect.x = 0
        self.player.rect.y = 0
        self.state = "WAVE"

    def update(self):
        keys = pg.key.get_pressed()

        match self.state:
            case "HOME":
                self.state = "INFO"

            case "WAVE":
                if keys[pg.K_i]:
                    self.state = "INFO"
                    self.prev_state = "WAVE"

                last_tick = self.clock.get_time()

                self.player.update(last_tick)
                self.enemy_manager.update(last_tick)

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
                    self.enemy_manager.load_enemies_for_wave(self.curr_wave)
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
        self.enemy_manager.load_enemies_for_wave(self.curr_wave)
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
