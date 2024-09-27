import pygame
import random
import upgrade
from max_health_upgrade import MaxHealthUpgrade
from num_ecto_upgrade import NumEctoUpgrade
from restore_health_upgrade import RestoreHealthUpgrade


class Shop:
    _instance = None
    rect = pygame.Rect(200, 200, 600, 200)

    upgrades: list[upgrade.Upgrade] = [
        MaxHealthUpgrade(),
        NumEctoUpgrade(),
        RestoreHealthUpgrade()
    ]

    upgrade_1 = None
    upgrade_2 = None
    upgrade_3 = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def rand_upgrade(self) -> upgrade.Upgrade:
        return self.upgrades.pop(random.randint(0, len(self.upgrades) - 1))

    def get_upgrades(self):
        self.upgrade_1 = self.rand_upgrade()
        self.upgrade_2 = self.rand_upgrade()
        self.upgrade_3 = self.rand_upgrade()

        self.upgrade_1.set_position(self.rect.topleft)
        self.upgrade_2.set_position(self.rect.midtop)
        self.upgrade_3.set_position(self.rect.topright)

    def close(self):
        self.upgrade_1.bought = False
        self.upgrade_2.bought = False
        self.upgrade_3.bought = False

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
