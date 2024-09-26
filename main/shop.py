import pygame
import random
import upgrade
import max_health_upgrade as mhu
import num_ecto_upgrade as neu
import restore_health_upgrade as rhu


class Shop:
    shop_rect = pygame.Rect(0, 0, 1000, 800)
    upgrade_rect = pygame.Rect(200, 200, 600, 200)

    upgrades: list[upgrade.Upgrade] = [
        mhu.MaxHealthUpgrade(),
        neu.NumEctoUpgrade(),
        rhu.RestoreHealthUpgrade()
    ]

    upgrade_1 = None
    upgrade_2 = None
    upgrade_3 = None

    def rand_upgrade(self) -> upgrade.Upgrade:
        return self.upgrades.pop(random.randint(0, len(self.upgrades) - 1))

    def load_shop_upgrades(self):
        self.upgrade_1 = self.rand_upgrade()
        self.upgrade_2 = self.rand_upgrade()
        self.upgrade_3 = self.rand_upgrade()

        self.upgrade_1.set_position(self.upgrade_rect.topleft)
        self.upgrade_2.set_position(self.upgrade_rect.midtop)
        self.upgrade_3.set_position(self.upgrade_rect.topright)

    def close_shop(self):
        self.upgrades.append(self.upgrade_1)
        self.upgrades.append(self.upgrade_2)
        self.upgrades.append(self.upgrade_3)

    def update(self):
        self.upgrade_1.update()
        self.upgrade_2.update()
        self.upgrade_3.update()

    def draw(self, background):
        self.upgrade_1.draw(background)
        self.upgrade_2.draw(background)
        self.upgrade_3.draw(background)
