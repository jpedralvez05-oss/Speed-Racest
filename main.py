import pygame
import time
import math
import os
from pygame.math import Vector2
from util import scale_img, blit_rotate_center

pygame.init()
pygame.mixer.init()

BG = scale_img(pygame.image.load("img/background.png"), 0.9)
TRACK = scale_img(pygame.image.load("img/track.png"), 0.9)
TRACK_BORDER = scale_img(pygame.image.load("img/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = scale_img(pygame.transform.rotate(pygame.image.load("img/finish.png"), 45), 0.3)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (2180, 950)

CAR = scale_img(pygame.image.load("img/red-car.png"), 0.20)

ZOOM = 2
WIDTH = 1200
HEIGHT = 700

font = pygame.font.SysFont("Arial", 28)
font_large = pygame.font.SysFont("Arial", 42, bold=True)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Racest")

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


def format_time(seconds):
    if seconds is None:
        return "--:--.--"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    return f"{mins:02d}:{secs:02d}.{centis:02d}"


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
                # First time crossing — start the clock, don't count a lap yet
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


class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = (2100, 850)

def draw_tachometer(screen, player_car):
    # bottom-left
    center_x = 320
    center_y = HEIGHT - 120
    radius = 90

    pygame.draw.circle(screen, (30, 30, 30), (center_x, center_y), radius)
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius, 3)

    # Tick marks
    for i in range(0, 181, 30):
        angle = math.radians(180 - i)
        x1 = center_x + math.cos(angle) * (radius - 10)
        y1 = center_y - math.sin(angle) * (radius - 10)
        x2 = center_x + math.cos(angle) * radius
        y2 = center_y - math.sin(angle) * radius
        pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2), 2)

    # Needle logic
    rpm_ratio = player_car.rpm  

    angle = math.radians(180 - (rpm_ratio * 180))

    needle_length = radius - 20
    needle_x = center_x + math.cos(angle) * needle_length
    needle_y = center_y - math.sin(angle) * needle_length

    pygame.draw.line(screen, (255, 0, 0),(center_x, center_y),(needle_x, needle_y), 4)

    pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 5)

   
    rpm_value = int(rpm_ratio * 8000)
    rpm_text = font.render(f"{rpm_value} RPM", True, (255, 255, 255))
    text_rect = rpm_text.get_rect(center=(center_x, center_y + 40))
    screen.blit(rpm_text, text_rect)


def draw_speedometer(screen, player_car): #speedometer logic placeholder, touch me pls kung may assets na
    #relocate to bottom left for better visibility
    center_x = 120
    center_y = HEIGHT - 120
    radius = 90

    pygame.draw.circle(screen, (30, 30, 30), (center_x, center_y), radius)
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius, 3)

    # Tick marks
    for i in range(0, 181, 30):  # 0° to 180°
        angle = math.radians(180 - i)
        x1 = center_x + math.cos(angle) * (radius - 10)
        y1 = center_y - math.sin(angle) * (radius - 10)
        x2 = center_x + math.cos(angle) * radius
        y2 = center_y - math.sin(angle) * radius
        pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2), 2)


    #Needle logic 
    speed = abs(player_car.vel)

    max_speed = player_car.max_vel
    speed_ratio = min(speed / max_speed, 1)


    angle = math.radians(180 - (speed_ratio * 180))

    needle_length = radius - 20
    needle_x = center_x + math.cos(angle) * needle_length
    needle_y = center_y - math.sin(angle) * needle_length

    pygame.draw.line(screen, (255, 0, 0),(center_x, center_y), (needle_x, needle_y), 4)

    pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 5)

    speed_text = font.render(f"{int(speed * 20)} km/h", True, (255, 255, 255))
    text_rect = speed_text.get_rect(center=(center_x, center_y + 40))
    screen.blit(speed_text, text_rect)


def draw(screen, images, player_car):
    camera_offset = player_car.camera()
    world_surface = pygame.Surface((int(WIDTH / ZOOM), int(HEIGHT / ZOOM)))

    for img, pos in images:
        world_surface.blit(img, (pos[0] - camera_offset.x, pos[1] - camera_offset.y))

    world_surface.blit(FINISH, (FINISH_POS[0] - camera_offset.x,
                                FINISH_POS[1] - camera_offset.y))

    player_car.draw(world_surface, camera_offset)

    scaled = pygame.transform.scale(world_surface, (WIDTH, HEIGHT))
    screen.blit(scaled, (0, 0))

    # --- HUD ---
    if player_car.gear == -1:
        gear_display = "R"
    elif player_car.gear == 0:
        gear_display = "N"
    else:
        gear_display = str(player_car.gear)

    gear_text = font.render(f"Gear: {gear_display}", True, (255, 255, 255))
    speed_text = font.render(f"Speed: {abs(player_car.vel):.1f}", True, (255, 255, 255))
    rpm_text = font.render(f"RPM: {int(player_car.rpm * 100)}%", True, (255, 255, 255))

    # Lap timing HUD (top-right)
    lap_text = font.render(f"Lap: {player_car.lap}", True, (255, 255, 255))
    current_time_text = font.render(
        f"Time: {format_time(player_car.current_lap_time)}", True, (255, 255, 0))
    best_time_text = font.render(
        f"Best: {format_time(player_car.best_lap_time)}", True, (0, 220, 100))

    screen.blit(rpm_text, (10, 70))
    screen.blit(gear_text, (10, 10))
    screen.blit(speed_text, (10, 40))

    screen.blit(lap_text, (WIDTH - 160, 10))
    screen.blit(current_time_text, (WIDTH - 240, 40))
    screen.blit(best_time_text, (WIDTH - 240, 70))

    # Flash last lap time in the center for 3 seconds after completing a lap
    if player_car.last_lap_time is not None and player_car.finish_cooldown > 0:
        msg = font_large.render(
            f"Lap {player_car.lap}  {format_time(player_car.last_lap_time)}",
            True, (255, 220, 0))
        msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        screen.blit(msg, msg_rect)

    player_car.update_sound()
    draw_speedometer(screen, player_car)
    draw_tachometer(screen, player_car)
    pygame.display.update()


running = True
FPS = 60
clock = pygame.time.Clock()
images = [(BG, (0, 0)), (TRACK, (0, 0))]
player_car = PlayerCar(6, 4)

while running:
    clock.tick(FPS)

    player_car.update_lap()
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
        player_car.reduce_speed()

    if player_car.track_collision(TRACK_BORDER_MASK) is not None:
        player_car.x = prev_x
        player_car.y = prev_y
        player_car.angle = prev_angle
        player_car.bounce()

pygame.quit()