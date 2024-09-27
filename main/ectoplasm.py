import pygame
from pygame import Vector2


class Ectoplasm:
    rect: pygame.Rect = None
    sprite: pygame.Surface = None
    direction: pygame.Vector2 = None
    speed = 10
    velocity: pygame.Vector2 = None
    is_active = True
    is_collected = False
    distance_traveled = 0
    max_range = 250

    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x + 8, y + 8, 16, 16)
        self.sprite = pygame.image.load("../assets/sprites/player/ectoplasm.png")
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

    def draw(self, background: pygame.Surface):
        background.blit(self.sprite, Vector2(self.rect.x, self.rect.y))
