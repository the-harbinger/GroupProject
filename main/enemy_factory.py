import pygame
from pygame import Vector2
import enemy


class EnemyFactory:
    _instance = None
    enemy_types = ["Tower"]
    times_called = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def create_enemy(cls) -> enemy.Enemy:
        e = enemy.Enemy(50, 50, 2, 10, Vector2(50 * cls.times_called, 50 * cls.times_called))
        cls.times_called += 1
        return e
