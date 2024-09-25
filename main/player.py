import pygame
from pygame import Vector2


class Player:
    _instance = None
    rect = pygame.Rect(600, 400, 32, 32)
    sprite = pygame.Surface((32, 32))
    velocity = Vector2(0, 0)
    speed = 3
    num_coins = 0
    num_ecto = 5
    max_num_ecto = 5
    phase_speed_modifier = 1.5
    phase_time = 0.33
    max_health = 10
    health = 10

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.sprite = pygame.image.load("../assets/sprites/player/ghost_player.png").convert_alpha()
        return cls._instance

    def update(self, last_tick: int):
        keys = pygame.key.get_pressed()

        x_strength = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        y_strength = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        direction = Vector2(x_strength, y_strength)
        if x_strength != 0 or y_strength != 0:
            direction = direction.normalize()

        self.velocity = self.speed * direction
        self.rect = self.rect.move(self.velocity)

    def draw(self, background: pygame.Surface):
        background.blit(self.sprite, (self.rect.x, self.rect.y))
