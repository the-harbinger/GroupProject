import pygame
import sys
import player as player_class
import enemy_manager as em


class Game:
    pygame.init()
    pygame.display.set_caption("Postmaster Arena")

    _instance = None
    player = None
    enemy_manager = None
    width = 1200
    height = 800

    bg = pygame.Surface((width, height - 100))
    screen = pygame.display.set_mode((width, height))
    screen.fill("Red")
    clock = pygame.time.Clock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def update(self):
        self.player.update()
        # TODO Update the UI

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.player.draw(self.screen)
        # TODO Draw the UI
        pygame.display.update()

    def start(self) -> None:
        self.player = player_class.Player.get_instance()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.update()
            self.draw()
            self.clock.tick(60)
