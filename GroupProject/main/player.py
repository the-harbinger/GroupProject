import pygame
from pygame import Vector2
from enum import Enum


class Player:
    class Animations(Enum):
        RUNNING = 0

    _instance = None
    sprites = [[]]
    rects = [[]]
    curr_animation: list[pygame.Surface] = []
    animation_ind = 0
    last_draw = 0
    pos = Vector2(0, 0)
    velocity = Vector2(0, 0)
    speed = 3
    melee_damage = 5
    num_messages = 5
    max_num_messages = 5
    slide_speed_modifier = 1.5
    slide_length = 0.33
    max_health = 10
    health = 10
    look_left = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.__load_animations()
            cls._instance.curr_animation = cls.sprites[cls.Animations.RUNNING.value]
        return cls._instance

    def __load_animations(self):
        sprite_sheet = pygame.image.load("../assets/sprites/player/player_running.png").convert_alpha()
        for x in range(8):
            rect = pygame.Rect((48 * x, 0), (48, 48))
            img_rect = sprite_sheet.subsurface(rect)
            self.sprites[self.Animations.RUNNING.value].append(img_rect)
            self.rects[self.Animations.RUNNING.value].append(rect)

    def get_hurtbox(self) -> pygame.Rect:
        return self.curr_animation[self.animation_ind].get_rect()

    def get_frame(self) -> pygame.Surface:
        if self.last_draw >= 60:
            self.animation_ind += 1
            self.last_draw = 0
        if self.animation_ind >= len(self.curr_animation):
            self.animation_ind = 0
        return self.curr_animation[self.animation_ind]

    def update(self):
        keys = pygame.key.get_pressed()

        x_strength = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        y_strength = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        direction = Vector2(x_strength, y_strength)
        if x_strength != 0 or y_strength != 0:
            direction = direction.normalize()

        self.velocity = self.speed * direction
        self.pos += self.velocity

        if self.velocity.x < 0:
            self.look_left = True
        elif self.velocity.x > 0:
            self.look_left = False

    def draw(self, screen, clock: pygame.time.Clock):
        self.last_draw += clock.get_time()
        frame = self.get_frame()
        if self.look_left:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (self.pos.x, self.pos.y))
