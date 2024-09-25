import pygame
import player as player_class
import enemy_manager as em


class Game:
    pygame.init()
    pygame.display.set_caption("Ecto-Blast-Em")

    _instance = None
    player = None
    enemy_manager = None
    width = 1200
    height = 800
    RUNNING = True
    curr_wave = 1
    MAX_WAVES = 2
    background: pygame.Surface = pygame.Surface((width, height - 100))
    screen = pygame.display.set_mode((width, height))
    screen.fill("Red")
    clock = pygame.time.Clock()
    state = "INFO"
    prev_state = "WAVE"

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

                    if self.curr_wave < self.MAX_WAVES:
                        self.state = "SHOP"
                    else:
                        self.state = "GAME_OVER"

            case "SHOP":
                if keys[pygame.K_i]:
                    self.state = "INFO"
                    self.prev_state = "SHOP"

                if keys[pygame.K_SPACE]:
                    self.curr_wave += 1
                    self.enemy_manager.load_enemies_for_wave(self.curr_wave)
                    self.state = "WAVE"

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
                # TODO IMPLEMENT SHOP CLASS
                self.screen.blit(self.background, (0, 0))
                self.background.fill("Yellow")

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
        pygame.display.update()

    def start(self) -> None:
        self.player = player_class.Player.get_instance()
        self.enemy_manager = em.EnemyManager.get_instance()
        self.enemy_manager.load_enemies_for_wave(self.curr_wave)

        while self.RUNNING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.RUNNING = False

            if self.RUNNING:
                self.update()
                self.draw()
                self.clock.tick(60)
