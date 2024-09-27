import pygame
import upgrade


class MaxHealthUpgrade(upgrade.Upgrade):
    def __init__(self):
        super().__init__()
        self.cost = 5
        self.card = pygame.image.load("../assets/UI/mhu_card.png")

    def update(self):
        if self.bought or not self.rect.collidepoint(pygame.mouse.get_pos()):
            self.clicked = False
            return

        pressed = pygame.mouse.get_pressed()[0]
        if pressed:
            self.clicked = True
            pygame.time.wait(120)

        if self.clicked and not pressed:
            if self.player.num_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.player.max_health += 1
                self.bought = True
            self.clicked = False

    def draw(self, background: pygame.Surface):
        super().draw(background)
