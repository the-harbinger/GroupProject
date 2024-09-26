import pygame
import player as pl


# Parent class for all upgrades bought in the shop
class Upgrade:
    player = None
    cost = 0
    rect: pygame.Rect = None
    card: pygame.Surface = None
    clicked = False

    def __init__(self):
        self.rect = pygame.Rect(0, 0, 200, 200)
        self.player = pl.Player.get_instance()

    def set_position(self, position: tuple):
        self.rect.x = position[0]
        self.rect.y = position[1]

    def update(self):
        pass

    def draw(self, background: pygame.Surface):
        background.blit(self.card, (self.rect.x, self.rect.y))
