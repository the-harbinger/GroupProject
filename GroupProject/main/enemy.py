import pygame
from pygame import Vector2
import game as game_class
import player as player_class


class Enemy:
    game = None
    player: player_class.Player = None
    x_pos = 50
    y_pos = 50
    sprite = pygame.Surface((50, 50))
    hitbox: pygame.Rect = sprite.get_rect(midbottom=(x_pos, y_pos))

    def __init__(self):
        self.game = game_class.Game.get_instance()
        self.player = player_class.Player.get_instance()
        return

    def update(self):
        print("MADE IT")
        if self.hitbox.colliderect(self.player.get_hurtbox()):
            print(True)

    def draw(self):
        self.sprite.fill('Red')
        self.game.screen.blit(self.sprite, self.hitbox)
