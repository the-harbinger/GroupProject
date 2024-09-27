import pygame
from pygame import Vector2
from player import Player
import random


class Enemy:
    game = None
    player: Player = None
    rect: pygame.Rect = pygame.Rect(0, 0, 50, 50)
    sprite: pygame.Surface = pygame.Surface((50, 50))
    difficulty = 0
    health = 0
    speed = 3
    velocity: Vector2 = None
    is_environmental = False
    color = None

    def __init__(self, width, height, difficulty, health, start_pos: Vector2):
        self.player = Player.get_instance()
        self.rect = pygame.Rect(start_pos.x, start_pos.y, width, height)
        self.difficulty = difficulty
        self.health = health
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self):
        slope_y = self.player.rect.centery - self.rect.centery
        slope_x = self.player.rect.centerx - self.rect.centerx

        direction = Vector2(slope_x, slope_y)

        if slope_y != 0 or slope_x != 0:
            direction = direction.normalize()

        self.velocity = direction * self.speed
        self.rect = self.rect.move(self.velocity)

        for e in self.player.ectos:
            if e.rect.colliderect(self.rect) and e.is_active:
                e.handle_enemy_hit()
                self.health -= 10

    def draw(self, background: pygame.Surface):
        self.sprite.fill(self.color)
        background.blit(self.sprite, (self.rect.x, self.rect.y))
