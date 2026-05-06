from app.car.player_car import AbstractCar
import math
from app.core import config


class EnemyCar(AbstractCar):
    def __init__(self, max_vel, rotation_vel, path, img):
        self.path = path
        self.current_point = 1
        self.IMG = img
        self.START_POS = self.path[0]
        super().__init__(max_vel, rotation_vel)

        target_x, target_y = self.path[self.current_point]
        dx = target_x - self.x
        dy = target_y - self.y
        self.angle = math.degrees(math.atan2(-dx, -dy))

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        dx = target_x - self.x
        dy = target_y - self.y
        # Correct Pygame coordinate math without the 180-degree flip
        desired_angle = math.degrees(math.atan2(-dx, -dy))
        angle_diff = (desired_angle - self.angle + 180) % 360 - 180
        return angle_diff

    def update_path_point(self):
        target_x, target_y = self.path[self.current_point]
        distance = math.hypot(target_x - self.x, target_y - self.y)
        if distance < 50:
            self.current_point = (self.current_point + 1) % len(self.path)

    def move_enemy(self):
        angle_diff = self.calculate_angle()
        if angle_diff > 5:
            self.rotate(left=True)
        elif angle_diff < -5:
            self.rotate(right=True)
        if abs(angle_diff) > 30:
            self.vel = max(self.vel - self.acceleration,
                           self.max_vel * 0.5)
        else:
            self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()
        self.update_path_point()

enemy_car = EnemyCar(5, 4, config.enemy_path, config.ENEMY_CAR)
enemy_car_2 = EnemyCar(4.5, 4, config.enemy_path_2, config.ENEMY_CAR_2)