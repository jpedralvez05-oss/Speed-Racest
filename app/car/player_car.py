from app.core import config
from app.core.config import idle_sound, fifth_gear_play, second_gear_play, third_gear_play, fourth_gear_play, first_gear_play, gear_down_sound, gear_up_sound, TRACK, WIDTH, ZOOM, HEIGHT, FINISH_MASK, FINISH_POS
from app.core.util import blit_rotate_center
import pygame, math, time
from pygame.math import Vector2

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.vel_drift = Vector2(0, 0)
        self.grip = 0.06
        self.rotation_vel = rotation_vel
        self.angle = 220
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.engine_state = "idle"
        self.rpm = 0
        self.rpm_redline = 0.9
        self.rpm_min = 0.2
        self.lap = 0
        self.lap_start_time = None
        self.current_lap_time = 0.0
        self.best_lap_time = None
        self.last_lap_time = None
        self.on_finish = False
        self.finish_cooldown = 0
        self.gear = 1
        self.gear_ratio = {-1: 0.25, 0: 0.0, 1: 0.25,
                           2: 0.45, 3: 0.65, 4: 0.85, 5: 1.0}
        self.gear_sound_dict = {
            "idle": idle_sound, "driving": [
                first_gear_play,
                second_gear_play,
                third_gear_play,
                fourth_gear_play,
                fifth_gear_play
            ]}
        self.engine_channel = pygame.mixer.Channel(0)
        self.current_sound = None

    def reset_pos(self):
        self.x, self.y = self.START_POS
        self.angle = 220

    def reset_time(self):
        self.lap_start_time = None
        self.current_lap_time = 0.0
        self.on_finish = False
        self.finish_cooldown = 0

    def car_sound(self, sound):
        if self.current_sound != sound:
            self.engine_channel.stop()
            self.current_sound = sound
        if not self.engine_channel.get_busy():
            self.engine_channel.play(sound, loops=-1)

    def get_driving_sound_and_volume(self):
        gear_to_be_played = self.gear_sound_dict["driving"]
        if self.gear in [-1, 0, 1]:
            index = 0
            volume = 0.2
        elif self.gear == 2:
            index = 1
            volume = 0.4
        elif self.gear == 3:
            index = 2
            volume = 0.6
        elif self.gear == 4:
            index = 3
            volume = 0.8
        else:
            index = 4
            volume = 1.0
        index = max(0, min(index, len(gear_to_be_played) - 1))
        return gear_to_be_played[index], volume

    def car_gear(self, new_gear, sound):
        if self.gear != new_gear:
            self.gear = new_gear
            pygame.mixer.Channel(1).play(sound)

    def gear_up(self):
        if self.gear < 5:
            if self.rpm >= 0.8 or self.gear <= 0:
                self.car_gear(self.gear + 1, gear_up_sound)

    def gear_down(self):
        if self.gear > -1:
            next_gear = self.gear - 1
            next_gear_max = self.max_vel * self.gear_ratio.get(next_gear, 0)
            if next_gear_max > 0:
                projected_rpm = self.rpm_min + \
                    (abs(self.vel) / next_gear_max) * (1.0 - self.rpm_min)
            else:
                projected_rpm = self.rpm_min
            if projected_rpm <= self.rpm_redline:
                self.car_gear(next_gear, gear_down_sound)

    def update_sound(self):
        if self.engine_state == "idle":
            target_sound = self.gear_sound_dict["idle"]
            target_volume = 0.2
        else:
            target_sound, target_volume = self.get_driving_sound_and_volume()
        if self.current_sound != target_sound:
            self.engine_channel.stop()
            self.current_sound = target_sound
        self.engine_channel.set_volume(target_volume)
        if not self.engine_channel.get_busy():
            self.engine_channel.play(target_sound, loops=-1)

    def gear_max(self):
        return self.max_vel * self.gear_ratio[self.gear]

    def rpm_update(self):
        target_vel = self.gear_max()
        if target_vel > 0:
            target_rpm = self.rpm_min + \
                (abs(self.vel) / target_vel) * (1.0 - self.rpm_min)
        else:
            target_rpm = self.rpm_min
        target_rpm = max(self.rpm_min, min(target_rpm, 1.0))
        if target_rpm > self.rpm:
            self.rpm += min(0.02, target_rpm - self.rpm)
        else:
            self.rpm += max(-0.01, target_rpm - self.rpm)

    def rpm_torque(self):
        if self.rpm < 0.4:
            return 0.6
        elif self.rpm < self.rpm_redline:
            return 1.0
        else:
            return 0.7

    def drive_gear(self):
        if self.gear == 0:
            self.reduce_speed()
            self.engine_state = "idle"
            return
        target_vel = self.gear_max()
        self.engine_state = "driving"
        if self.gear > 0:
            if self.vel < 0:
                self.vel = min(self.vel + self.acceleration * 2, 0)
            elif self.vel < target_vel:
                gear_accel = self.acceleration * (0.5 + self.gear * 0.2)
                speed_ratio = 1 - \
                    (self.vel / target_vel) if target_vel > 0 else 0
                self.vel = min(self.vel + gear_accel *
                               speed_ratio * self.rpm_torque(), target_vel)
            else:
                self.vel = max(self.vel - self.acceleration * 0.5, target_vel)
        elif self.gear == -1:
            if self.vel > 0:
                self.vel = max(self.vel - self.acceleration * 2, 0)
            elif abs(self.vel) < target_vel:
                gear_accel = self.acceleration * 0.5
                speed_ratio = 1 - \
                    (abs(self.vel) / target_vel) if target_vel > 0 else 0
                self.vel = max(self.vel - gear_accel *
                               speed_ratio * self.rpm_torque(), -target_vel)
            else:
                self.vel = min(self.vel + self.acceleration * 0.5, -target_vel)
        self.move()

    def brake(self):
        self.engine_state = "idle"
        brake_force = self.max_vel * 0.02
        if self.vel > 0:
            self.vel = max(self.vel - brake_force, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + brake_force, 0)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        direction_x = math.sin(radians)
        direction_y = math.cos(radians)
        target_velocity = Vector2(
            direction_x * self.vel, direction_y * self.vel)
        self.vel_drift = self.vel_drift.lerp(target_velocity, self.grip)
        self.y -= self.vel_drift.y
        self.x -= self.vel_drift.x
        limit_move_x = TRACK.get_width() - self.img.get_width()
        limit_move_y = TRACK.get_height() - self.img.get_height()
        self.x = max(0, min(self.x, limit_move_x))
        self.y = max(0, min(self.y, limit_move_y))
        if self.x == 0 or self.x == limit_move_x or self.y == 0 or self.y == limit_move_y:
            self.vel = 0
            self.vel_drift = Vector2(0, 0)
        self.rpm_update()

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def reduce_speed(self):
        self.engine_state = "idle"
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.acceleration / 2, 0)
        self.move()

    def draw(self, screen, camera_offset):
        draw_pos = (self.x - camera_offset.x, self.y - camera_offset.y)
        blit_rotate_center(screen, self.img, draw_pos, self.angle)

    def camera(self):
        screen_center = Vector2((WIDTH / ZOOM) / 2, (HEIGHT / ZOOM) / 2)
        car_center = Vector2(self.x + self.img.get_width() / 2,
                             self.y + self.img.get_height() / 2)
        offset = car_center - screen_center
        offset.x = max(0, min(offset.x, TRACK.get_width() - (WIDTH / ZOOM)))
        offset.y = max(0, min(offset.y, TRACK.get_height() - (HEIGHT / ZOOM)))
        return offset

    def track_collision(self, mask, x=0, y=0):
        rotated_image = pygame.transform.rotate(self.img, self.angle)
        rect_collision = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        car_mask = pygame.mask.from_surface(rotated_image)
        offset = (int(rect_collision.x - x), int(rect_collision.y - y))
        overlap_checker = mask.overlap(car_mask, offset)
        return overlap_checker

    def bounce(self):
        self.vel = -self.vel * 0.8
        self.vel_drift = -self.vel_drift * 0.8
        self.move()

    def update_lap(self):
        now = time.time()
        # Count down the re-arm cooldown
        if self.finish_cooldown > 0:
            self.finish_cooldown -= 1
        touching = self.track_collision(FINISH_MASK, *FINISH_POS) is not None
        if touching and not self.on_finish and self.finish_cooldown == 0 and self.vel > 0:
            self.on_finish = True
            self.finish_cooldown = 90
            if self.lap_start_time is None:
                # First time crossing   start the clock, don't count a lap yet
                self.lap_start_time = now
            else:
                elapsed = now - self.lap_start_time
                self.last_lap_time = elapsed
                if self.best_lap_time is None or elapsed < self.best_lap_time:
                    self.best_lap_time = elapsed
                self.lap += 1
                self.lap_start_time = now
        elif not touching:
            self.on_finish = False
        # Update running lap time
        if self.lap_start_time is not None:
            self.current_lap_time = now - self.lap_start_time

def get_speed_angle(player_car):
    speed = abs(player_car.vel)
    max_speed = player_car.max_vel

    ratio = min(speed / max_speed, 1)

    # Map 0 → 180°  and 1 → 0°
    return math.radians(180 - (ratio * 180))


class PlayerCar(AbstractCar):
    IMG = config.CAR
    START_POS = (2180, 950)

    def __init__(self, max_vel, rotation_vel):
        super().__init__(max_vel, rotation_vel)

player_car = PlayerCar(6, 4)