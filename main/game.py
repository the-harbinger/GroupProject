import pygame
from player import Player
from enemy_manager import EnemyManager
from shop import Shop


class Game:
    pygame.init()
    pygame.display.set_caption("Ecto-Blast-Em")

    _instance = None
    player = None
    enemy_manager = None
    shop = None
    width = 1200
    height = 800
    RUNNING = True
    curr_wave = 1
    MAX_WAVES = 3
    background: pygame.Surface = pygame.Surface((width, height - 100))
    screen = pygame.display.set_mode((width, height))
    screen.fill("Red")
    clock = pygame.time.Clock()
    state = "HOME"
    prev_state = "WAVE"
    cursor = None
    cursor_rect = pygame.Rect(0, 0, 16, 16)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def restart_game(self):
        # TODO IMPLEMENT PROPERLY
        self.curr_wave = 1
        self.enemy_manager.load_enemies_for_wave(self.curr_wave)
        self.player.rect.x = 0
        self.player.rect.y = 0
        self.state = "WAVE"

    def update(self):
        keys = pygame.key.get_pressed()

        match self.state:
            case "HOME":
                self.state = "INFO"

            case "WAVE":
                if keys[pygame.K_i]:
                    self.state = "INFO"
                    self.prev_state = "WAVE"

                last_tick = self.clock.get_time()

                self.player.update(last_tick)
                self.enemy_manager.update(last_tick)

                if self.player.health < 0:
                    self.state = "GAME_OVER"

                if self.enemy_manager.wave_complete:
                    self.player.rect.x = self.width / 2
                    self.player.rect.y = self.height / 2
                    self.player.num_ecto = 0
                    self.player.ectos = []

                    if self.curr_wave < self.MAX_WAVES:
                        self.shop.get_upgrades()
                        self.state = "SHOP"
                    else:
                        self.state = "GAME_OVER"

            case "SHOP":
                if keys[pygame.K_i]:
                    self.state = "INFO"
                    self.prev_state = "SHOP"

                if keys[pygame.K_SPACE]:
                    self.shop.close()
                    self.curr_wave += 1
                    self.enemy_manager.load_enemies_for_wave(self.curr_wave)
                    self.state = "WAVE"

                self.shop.update()

            case "INFO":
                if keys[pygame.K_e]:
                    self.state = self.prev_state

            case "GAME_OVER":
                if keys[pygame.K_SPACE]:
                    self.restart_game()
                if keys[pygame.K_e]:
                    self.RUNNING = False

        # TODO Update the UI

    def draw(self):
        match self.state:
            case "WAVE":
                self.screen.blit(self.background, (0, 0))
                self.background.fill("Black")
                self.player.draw(self.background)
                self.enemy_manager.draw(self.background)

            case "SHOP":
                self.screen.blit(self.background, (0, 0))
                self.background.fill("Black")
                self.shop.draw(self.background)
                self.screen.blit(self.cursor, pygame.mouse.get_pos())

            case "INFO":
                # TODO CREATE INFO SCREEN
                self.screen.blit(self.background, (0, 0))
                self.background.fill("Cyan")

            case "GAME_OVER":
                # TODO CREATE GAME OVER SCREEN
                # TODO Show Victory or Defeat Screen Based on Player Health
                self.screen.blit(self.background, (0, 0))
                self.background.fill("Green")

        # TODO Draw the UI
        pygame.display.flip()

    def start(self) -> None:
        # Create instances of Game Objects
        pygame.mouse.set_visible(False)
        self.player = Player.get_instance()
        self.enemy_manager = EnemyManager.get_instance()
        self.shop = Shop().get_instance()
        self.enemy_manager.load_enemies_for_wave(self.curr_wave)
        self.cursor = pygame.image.load("../assets/sprites/player/cursor.png")

        while self.RUNNING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.RUNNING = False

            if self.RUNNING:
                self.update()
                self.draw()
                self.clock.tick(60)
