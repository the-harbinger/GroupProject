import pygame
import player as player_class
import game as game_class


class UI:
    game = None
    width = 0
    height = 0
    surf: pygame.Surface = None
    rect: pygame.Rect = None
    player = None

    def __init__(self):
        self.game = game_class.Game.get_instance()
        self.player = player_class.Player.get_instance()
        self.width = self.game.width
        self.height = 100
        self.surf = pygame.Surface(self.width, self.height)
        self.surf.fill("Red")

    def update(self):
        pass

    def draw(self):
        pass
