import pygame
from pygame import Vector2
import game as game_class
import player as player_class


class Enemy:
    game = None
    player: player_class.Player = None
    rect: pygame.Rect = pygame.Rect(0, 0, 50, 50)
    sprite: pygame.Surface = pygame.Surface((50, 50))

    def __init__(self, width, height, pos: pygame.Vector2):
        self.game = game_class.Game.get_instance()
        self.player = player_class.Player.get_instance()
        self.rect = pygame.Rect(pos.x, pos.y, width, height)

    def update(self):
        pass

    def draw(self):
        pass
