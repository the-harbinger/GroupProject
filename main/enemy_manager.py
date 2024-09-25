import pygame
import enemy
import enemy_factory


def get_difficulty(curr_wave: int):
    match curr_wave:
        case 1:
            return 5
        case 2:
            return 7
        case 3:
            return 12
        case 4:
            return 18
        case 5:
            return 25


def get_spawn_rate(curr_wave: int):
    match curr_wave:
        case 1:
            return 900
        case 2:
            return 800
        case 3:
            return 700
        case 4:
            return 600
        case 5:
            return 500


class EnemyManager:
    _instance = None
    unspawned_enemies: list[enemy.Enemy] = []
    spawned_enemies: list[enemy.Enemy] = []
    difficulty = 0
    spawn_rate = 0
    last_spawn = 0
    wave_complete = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def load_enemies_for_wave(self, curr_wave: int):
        self.spawn_rate = get_spawn_rate(curr_wave)
        self.difficulty = get_difficulty(curr_wave)
        self.last_spawn = 0
        self.wave_complete = False
        self.__create_enemies()

    def __create_enemies(self):
        while self.difficulty > 0:
            e = enemy_factory.EnemyFactory.create_enemy()

            if e.is_environmental:
                self.spawned_enemies.append(e)
            else:
                self.unspawned_enemies.append(e)

            self.difficulty -= e.difficulty

    def update(self, last_tick: int):
        enemies_to_keep: list[enemy] = []

        for e in self.spawned_enemies:
            e.update()
            if e.health > 0:
                enemies_to_keep.append(e)

        self.spawned_enemies = enemies_to_keep
        self.last_spawn += last_tick

        len_unspawned = len(self.unspawned_enemies)
        len_spawned = len(self.spawned_enemies)

        if self.last_spawn >= self.spawn_rate and len_unspawned > 0:
            self.spawned_enemies.append(self.unspawned_enemies.pop(0))
            self.last_spawn = 0

        if len_unspawned <= 0 and len_spawned <= 0:
            self.wave_complete = True

    def draw(self, background: pygame.Surface):
        for e in self.spawned_enemies:
            e.draw(background)
