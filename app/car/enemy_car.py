from app.car.player_car import AbstractCar
from app.core.config import ENEMY_CAR, enemy_path
from pygame.math import Vector2
import math


class EnemyCar(AbstractCar):
    def __init__(self, max_vel, rotation_vel, path, img):
        self.path = path
        self.current_point = 1
        self.IMG = img
        self.START_POS = (self.path[0][0] - img.get_width() / 2, self.path[0][1] - img.get_height() / 2)
        super().__init__(max_vel, rotation_vel)
        self.grip = 0.55
        self.path_radius = 14
        self.gear = 1
        self.rpm = self.rpm_min
        self.engine_state = "driving"
        self.brake_deceleration = 0.12
        self.close_player_distance = 170
        self.safe_player_distance = 360
        self.far_player_distance = 650

        self.gear_ratio = {-1: 0.18, 0: 0.0, 1: 0.22,
                           2: 0.39, 3: 0.56, 4: 0.72, 5: 0.88}
        self.max_speed_per_gear = {
            gear: self.max_vel * ratio
            for gear, ratio in self.gear_ratio.items()
            if gear > 0
        }
        self.acceleration_limits = {
            1: 0.055,
            2: 0.065,
            3: 0.075,
            4: 0.085,
            5: 0.095,
        }

        target = self.get_target()
        center = self.get_center()
        dx = target.x - center.x
        dy = target.y - center.y
        self.angle = math.degrees(math.atan2(-dx, -dy))

    def get_center(self):
        return Vector2(self.x + self.img.get_width() / 2,
                       self.y + self.img.get_height() / 2)

    def get_player_distance(self, player_car):
        player_center = Vector2(player_car.x + player_car.img.get_width() / 2,
                                player_car.y + player_car.img.get_height() / 2)
        return self.get_center().distance_to(player_center)

    def get_target(self):
        return Vector2(self.path[self.current_point])

    def gear_max(self):
        if self.gear <= 0:
            return 0
        return self.max_speed_per_gear[self.gear]

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

    def get_corner_speed(self, turn_amount):
        if turn_amount > 55:
            return self.max_speed_per_gear[1]
        if turn_amount > 25:
            return self.max_speed_per_gear[2]
        if turn_amount > 10:
            return self.max_speed_per_gear[4] * 0.9
        return self.max_speed_per_gear[5]

    def get_distance_speed_factor(self, player_car):
        distance = self.get_player_distance(player_car)
        if distance < self.close_player_distance:
            return 0.45
        if distance < self.safe_player_distance:
            return 0.68
        if distance < self.far_player_distance:
            return 0.84
        return 1.0

    def choose_target_gear(self, target_vel):
        for gear in range(1, 6):
            if target_vel <= self.max_speed_per_gear[gear]:
                return gear
        return 5

    def shift_toward_target(self, target_vel):
        target_gear = self.choose_target_gear(target_vel)
        if target_gear > self.gear and self.rpm >= 0.78:
            self.gear += 1
        elif target_gear < self.gear and (
            self.rpm <= 0.55 or
            target_vel < self.gear_max() * 0.7 or
            self.vel > target_vel * 1.2
        ):
            self.gear -= 1

    def drive_toward_speed(self, target_vel):
        self.shift_toward_target(target_vel)
        gear_cap = self.gear_max()
        target_vel = min(target_vel, gear_cap)
        if self.vel < target_vel:
            gear_accel = self.acceleration_limits[self.gear]
            speed_ratio = 1 - (self.vel / gear_cap) if gear_cap > 0 else 0
            self.vel = min(
                self.vel + gear_accel * speed_ratio * self.rpm_torque(),
                target_vel
            )
        else:
            self.vel = max(self.vel - self.brake_deceleration, target_vel)

    def move_enemy(self, player_car):
        self.update_path_point()

        angle_diff = self.calculate_angle()
        turn = max(-self.rotation_vel, min(self.rotation_vel, angle_diff))
        self.angle += turn

        turn_amount = abs(angle_diff)
        target_vel = self.get_corner_speed(turn_amount)
        target_vel *= self.get_distance_speed_factor(player_car)
        self.drive_toward_speed(target_vel)

        if turn_amount > 30:
            self.vel_drift *= 0.75

        self.move()
        self.update_path_point()

enemy_car = EnemyCar(5, 4, enemy_path, ENEMY_CAR)
