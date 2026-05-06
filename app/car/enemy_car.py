from app.car.player_car import AbstractCar
from app.core.config import WIDTH, HEIGHT, ZOOM, ENEMY_CAR, GAUGE_IMG, FINISH_POS, FINISH, font_large, enemy_path, font
from app.core.util import format_time
from pygame.math import Vector2
import math, pygame


class EnemyCar(AbstractCar):
    def __init__(self, max_vel, rotation_vel, path, img):
        self.path = path
        self.current_point = 1
        self.IMG = img
        self.START_POS = (self.path[0][0] - img.get_width() / 2, self.path[0][1] - img.get_height() / 2)
        super().__init__(max_vel, rotation_vel)
        self.grip = 0.55
        self.path_radius = 14
        self.acceleration = 0.08

        target = self.get_target()
        center = self.get_center()
        dx = target.x - center.x
        dy = target.y - center.y
        self.angle = math.degrees(math.atan2(-dx, -dy))

    def get_center(self):
        return Vector2(self.x + self.img.get_width() / 2,
                       self.y + self.img.get_height() / 2)

    def get_target(self):
        return Vector2(self.path[self.current_point])

    def calculate_angle(self):
        target = self.get_target()
        center = self.get_center()
        dx = target.x - center.x
        dy = target.y - center.y
        desired_angle = math.degrees(math.atan2(-dx, -dy))
        angle_diff = (desired_angle - self.angle + 180) % 360 - 180
        return angle_diff

    def update_path_point(self):
        center = self.get_center()
        target = self.get_target()
        previous = Vector2(self.path[self.current_point - 1])
        segment = target - previous
        distance = center.distance_to(target)
        passed_target = False
        if segment.length_squared() > 0:
            passed_target = (center - target).dot(segment) > 0

        if distance < self.path_radius or passed_target:
            self.current_point = (self.current_point + 1) % len(self.path)

    def move_enemy(self):
        self.update_path_point()

        angle_diff = self.calculate_angle()
        turn = max(-self.rotation_vel, min(self.rotation_vel, angle_diff))
        self.angle += turn

        turn_amount = abs(angle_diff)
        if turn_amount > 55:
            target_vel = self.max_vel * 0.25
        elif turn_amount > 25:
            target_vel = self.max_vel * 0.45
        elif turn_amount > 10:
            target_vel = self.max_vel * 0.7
        else:
            target_vel = self.max_vel

        if self.vel < target_vel:
            self.vel = min(self.vel + self.acceleration, target_vel)
        else:
            self.vel = max(self.vel - self.acceleration * 1.5, target_vel)

        if turn_amount > 30:
            self.vel_drift *= 0.75

        self.move()
        self.update_path_point()

enemy_car = EnemyCar(5, 4, enemy_path, ENEMY_CAR)