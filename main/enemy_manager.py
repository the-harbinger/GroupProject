import pygame
import enemy


class EnemyManager:
    _instance = None
    enemies: list[enemy.Enemy] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def create_enemies(self):
        e = enemy.Enemy()
        self.enemies.append(e)

    def update(self):
        for e in self.enemies:
            e.update()

    def draw(self):
        for e in self.enemies:
            e.draw()
