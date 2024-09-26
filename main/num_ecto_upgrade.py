import pygame
import upgrade


class NumEctoUpgrade(upgrade.Upgrade):
    def __init__(self):
        super().__init__()
        self.cost = 5
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

        if self.clicked and not pressed and mouse_collides:
            if player_coins >= self.cost:
                self.player.num_coins -= self.cost
                self.player.max_num_ecto += 1
            else:
                print("Not enough Currency")
            self.clicked = False

    def draw(self, background: pygame.Surface):
        self.card.fill("Green")
        super().draw(background)
