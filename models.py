from pygame.math import Vector2
from utils import *
from pygame.transform import rotozoom
import numpy as np

UP = Vector2(0, -1)


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)
        # print(self.velocity.magnitude())

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        # self.position = self.position + self.velocity
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius / 3


class Spaceship(GameObject):

    MANEUVERABILITY = 3
    ACCELERATION = 0.05
    BULLET_SPEED = 3

    def __init__(self, position, create_bullet_callback):
        self.create_bullet_callback = create_bullet_callback
        # Make a copy of the original UP vector
        self.direction = Vector2(UP)
        self.laser_sound = load_sound("laser")

        super().__init__(position, load_sprite("spaceship", scale_tuple=(50, 50)), Vector2(0))

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self, sign):
        old_vel = self.velocity
        new_vel = self.velocity + sign * self.direction * self.ACCELERATION
        if 0 <= new_vel.magnitude() < 10:
            self.velocity = new_vel
        # print(f'vel: {old_vel.magnitude()}, new_vel: {new_vel.magnitude()}')
        # if old_vel.magnitude() > 2 and new_vel.magnitude() < 2:
        #     self.velocity = Vector2(0)

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        self.laser_sound.play()


class Asteroid(GameObject):
    def __init__(self, position, create_asteroid_callback, size=3):
        self.create_asteroid_callback = create_asteroid_callback
        self.size = size
        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25,
        }
        scale = size_to_scale[size]
        sprite = rotozoom(load_sprite("asteroid"), 0, scale)

        super().__init__(position, sprite, get_random_velocity(1, 2))

    def split(self):
        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(self.position, self.create_asteroid_callback, self.size - 1)
                self.create_asteroid_callback(asteroid)


class Bullet(GameObject):
    def __init__(self, position, velocity):
        super().__init__(position, load_sprite("bullet", scale_tuple=(30, 30)), velocity)

    def move(self, surface):
        self.position = self.position + self.velocity


