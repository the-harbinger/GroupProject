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
    width = 800
    height = 400
    enemies = []

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def update(self):
        self.player.update()

    def draw(self):
        bg = pygame.Surface((self.width, self.height))
        bg.fill("White")
        self.screen.blit(bg, (0, 0))
        self.player.draw(self.screen, self.clock)
        self.enemy_manager.update()
        pygame.display.update()

    def start(self) -> None:
        self.player = player_class.Player.get_instance()
        self.enemy_manager = em.EnemyManager.get_instance()
        self.enemy_manager.create_enemy()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.update()
            self.draw()
            self.clock.tick(60)
