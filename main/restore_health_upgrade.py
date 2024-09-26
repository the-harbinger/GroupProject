import pygame
import upgrade


class RestoreHealthUpgrade(upgrade.Upgrade):
    def __init__(self):
        super().__init__()
        self.cost = 10
        self.card = pygame.Surface((self.rect.width, self.rect.height))

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_collides = self.rect.collidepoint(mouse_pos)

        if not mouse_collides:
            self.clicked = False
            return

        player_coins = self.player.num_coins
        pressed = pygame.mouse.get_pressed()[0]

        if pressed:
            self.clicked = True
            pygame.time.wait(120)

        if self.clicked and not pressed:
            if player_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.player.health = self.player.max_health
            else:
                print("Not enough Currency")
            self.clicked = False

    def draw(self, background: pygame.Surface):
        self.card.fill("Pink")
        super().draw(background)
