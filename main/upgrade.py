import pygame
from player import Player


# Parent class for all upgrades bought in the shop
class Upgrade:
    player = None
    cost = 0
    rect: pygame.Rect = None
    card: pygame.Surface = None
    clicked = False
    bought = False
    sold_card = pygame.image.load("../assets/UI/sold_card.png")

    def __init__(self):
        self.rect = pygame.Rect(0, 0, 200, 200)
        self.player = Player.get_instance()

    def set_position(self, position: tuple):
        self.rect.x = position[0]
        self.rect.y = position[1]

    def update(self):
        pass

    def draw(self, background: pygame.Surface):
        if self.bought:
            background.blit(self.sold_card, (self.rect.x, self.rect.y))
        else:
            background.blit(self.card, (self.rect.x, self.rect.y))
