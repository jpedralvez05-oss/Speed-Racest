import pygame
import time
import math
import os
from pygame.math import Vector2
from util import scale_img, blit_rotate_center

pygame.init()
pygame.mixer.init()

GRASS = scale_img(pygame.image.load("img/grass.jpg"), 4)
TRACK = scale_img(pygame.image.load("img/track.png"), 0.7)
TRACK_BORDER = scale_img(pygame.image.load("img/track-border.png"), 0.7)
# created a mask so it tracks the track border of the image
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("img/finish.png")

CAR = scale_img(pygame.image.load("img/red-car.png"), 0.20)

ZOOM = 2
WIDTH = 1200
HEIGHT = 700

font = pygame.font.SysFont("Arial", 28)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Racist")

GEAR_DOWN_PATH = os.path.join('sounds', 'gear_down.mp3')
GEAR_UP_PATH = os.path.join('sounds', 'gear_up.mp3')
IDLE_PATH = os.path.join('sounds', 'idle.mp3')

first_gear_sound = os.path.join('sounds/accelerate', 'first_gear.mp3')
second_gear_sound = os.path.join('sounds/accelerate', 'second_gear.mp3')
third_gear_sound = os.path.join('sounds/accelerate', 'third_gear.mp3')
fourth_gear_sound = os.path.join('sounds/accelerate', 'fourth_gear.mp3')
fifth_gear_sound = os.path.join('sounds/accelerate', 'fifth_gear.mp3')

gear_down_sound = pygame.mixer.Sound(GEAR_DOWN_PATH)
gear_up_sound = pygame.mixer.Sound(GEAR_UP_PATH)
idle_sound = pygame.mixer.Sound(IDLE_PATH)

first_gear_play = pygame.mixer.Sound(first_gear_sound)
second_gear_play = pygame.mixer.Sound(second_gear_sound)
third_gear_play = pygame.mixer.Sound(third_gear_sound)
fourth_gear_play = pygame.mixer.Sound(fourth_gear_sound)
fifth_gear_play = pygame.mixer.Sound(fifth_gear_sound)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.vel_drift = Vector2(0, 0)
        self.grip = 0.06
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.engine_state = "idle"
        self.rpm = 0  # self.rpm = self.vel / self.max_vel, replaced stale code with new rpm system
        self.rpm_redline = 0.9  # This is where the redline starts for the rpm ratio, basically the redline is line where the gear will start sustaining damage if redlined for too long
        self.rpm_min = 0.2  # The rpm's idle position

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

        # RPM rises faster than it falls (like a real engine)
        if target_rpm > self.rpm:
            self.rpm += min(0.02, target_rpm - self.rpm)  # rise rate
        else:
            self.rpm += max(-0.01, target_rpm - self.rpm)  # fall rate

    def rpm_torque(self):
        if self.rpm < 0.4:
            return 0.6  # low rpm
        elif self.rpm < self.rpm_redline:
            return 1.0  # max rpm
        else:
            return 0.7  # redline, power falls off

    # renamed function from neutral_gear to drive_gear, makes more sense since it handles all the gears from reverse to fifth.
    def drive_gear(self):
        if self.gear == 0:
            self.reduce_speed()
            self.engine_state = "idle"
            return

        target_vel = self.gear_max()
        self.engine_state = "driving"

        if self.gear > 0:  # Added new elif statement to make downshift slowly reduce speed to previous limit instead of snapping back
            if self.vel < 0:
                self.vel = min(self.vel + self.acceleration * 2, 0)
            elif self.vel < target_vel:
                gear_accel = self.acceleration * (0.5 + self.gear * 0.2)
                # Tapers acceleration when nearing velocity, makes it slightly more realistic
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

    # Removed move_forward since it is dead code.

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

        self.rpm_update()  # New rpm system update

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
            center=self.img.get_rect(topleft=(self.x, self.y)) .center)

        car_mask = pygame.mask.from_surface(
            rotated_image)  # mask for the rotated car
        # tracks the track mask and the car mask both its top left corner
        offset = (int(rect_collision.x - x), int(rect_collision.y - y))

        # checks if the pixels of the car mask touches the pixels of the track mask
        overlap_checker = mask.overlap(car_mask, offset)
        return overlap_checker

    def bounce(self):
        self.vel = -self.vel * 0.8
        self.vel_drift = -self.vel_drift * 0.8
        self.move()
        # bounce the car, reversing the cars direction
        # (0.8 is the percent that makes the car loses it's momentum when hitting the border)


class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = (250, 220)


def draw(screen, images, player_car):
    camera_offset = player_car.camera()
    world_surface = pygame.Surface((int(WIDTH / ZOOM), int(HEIGHT / ZOOM)))

    for img, pos in images:
        world_surface.blit(
            img, (pos[0] - camera_offset.x, pos[1] - camera_offset.y))

    player_car.draw(world_surface, camera_offset)

    scaled = pygame.transform.scale(world_surface, (WIDTH, HEIGHT))
    screen.blit(scaled, (0, 0))

    if player_car.gear == -1:
        gear_display = "R"
    elif player_car.gear == 0:
        gear_display = "N"
    else:
        gear_display = str(player_car.gear)

    gear_text = font.render(f"Gear: {gear_display}", True, (255, 255, 255))
    speed_text = font.render(
        f"Speed: {abs(player_car.vel):.1f}", True, (255, 255, 255))
    # Displays the rpm of the car
    rpm_text = font.render(
        f"RPM: {int(player_car.rpm * 100)}%", True, (255, 255, 255))

    screen.blit(rpm_text, (10, 70))
    screen.blit(gear_text, (10, 10))
    screen.blit(speed_text, (10, 40))

    player_car.update_sound()

    pygame.display.update()


running = True
FPS = 60
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0))]
player_car = PlayerCar(6, 4)

while running:
    clock.tick(FPS)

    draw(screen, images, player_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                player_car.gear_up()
            if event.key == pygame.K_k:
                player_car.gear_down()

    keys = pygame.key.get_pressed()
    moved = False

    prev_x = player_car.x
    prev_y = player_car.y
    prev_angle = player_car.angle

    # Not operator ensures when holding Gas and Break don't call move() twice, which caused a sudden jump in speed before breaking
    if keys[pygame.K_w] and not keys[pygame.K_SPACE]:
        moved = True
        player_car.drive_gear()
    if keys[pygame.K_SPACE]:
        moved = True
        player_car.brake()

    if keys[pygame.K_a] and player_car.vel != 0:
        player_car.rotate(left=True)

    if keys[pygame.K_d] and player_car.vel != 0:
        player_car.rotate(right=True)

    if not moved:
        # reduces speed when the user lets go of the "w" key to slow down just like irl
        player_car.reduce_speed()

    # this puts the car back in 1 frame when it hits the track border while still having the bounce effect
    # this prevents the car fromm getting stuck in the track border
    # uhh Im stuck stepsis
    if player_car.track_collision(TRACK_BORDER_MASK) is not None:
        player_car.x = prev_x
        player_car.y = prev_y
        player_car.angle = prev_angle
        player_car.bounce()


pygame.quit()
