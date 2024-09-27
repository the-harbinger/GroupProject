import pygame
from pygame import Vector2
from ectoplasm import Ectoplasm


class Player:
    _instance = None
    rect = pygame.Rect(600, 400, 32, 32)
    sprite = pygame.image.load("../assets/sprites/player/ghost_player.png")
    velocity = Vector2(0, 0)
    ectos: list[Ectoplasm] = []
    speed = 15
    num_coins = 15
    num_ecto = 0
    max_num_ecto = 5
    phase_speed_modifier = 1.5
    phase_time = 0.33
    max_health = 10
    health = 10
    shoot_pressed: bool = False
    shoot_direction: Vector2 = Vector2(0, -1)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def update(self, last_tick: int):
        # MOVE THE PLAYER
        keys = pygame.key.get_pressed()

        x_strength = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        y_strength = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        direction = Vector2(x_strength, y_strength)
        if x_strength != 0 or y_strength != 0:
            direction = direction.normalize()
            self.shoot_direction = direction

        desired_velocity: Vector2 = self.speed * direction
        steering_force = desired_velocity - self.velocity * 2.5
        self.velocity += (steering_force * (last_tick / 1000))

        # SHOOT ECTOPLASM
        c_pressed = keys[pygame.K_c]
        if c_pressed:
            self.shoot_pressed = True
        if not c_pressed and self.shoot_pressed and self.num_ecto < self.max_num_ecto:
            ecto = Ectoplasm(self.rect.x, self.rect.y, self.shoot_direction)
            self.ectos.append(ecto)
            self.shoot_pressed = False
            self.num_ecto += 1
        uncollected_ectos = []
        for ecto in self.ectos:
            if ecto.rect.colliderect(self.rect) and not ecto.is_active:
                ecto.is_collected = True
                self.num_ecto -= 1
            ecto.update()

            if not ecto.is_collected:
                uncollected_ectos.append(ecto)
            self.ectos = uncollected_ectos
        self.rect = self.rect.move(self.velocity)

    def draw(self, background: pygame.Surface):
        for ecto in self.ectos:
            ecto.draw(background)
        background.blit(self.sprite, (self.rect.x, self.rect.y))

