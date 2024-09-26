import pygame
from pygame import Vector2
import player as player_class


class Enemy:
    game = None
    player: player_class.Player = None
    rect: pygame.Rect = pygame.Rect(0, 0, 50, 50)
    sprite: pygame.Surface = pygame.Surface((50, 50))
    difficulty = 0
    health = 0
    is_environmental = False

    def __init__(self, width, height, is_environmental, difficulty, health, start_pos: Vector2):
        self.player = player_class.Player.get_instance()
        self.rect = pygame.Rect(start_pos.x, start_pos.y, width, height)
        self.is_environmental = is_environmental
        self.difficulty = difficulty
        self.health = health

    def update(self):
        if self.rect.colliderect(self.player.rect):
            self.health -= 10

    def draw(self, background: pygame.Surface):
        self.sprite.fill("Blue")
        background.blit(self.sprite, (self.rect.x, self.rect.y))