import pygame
import time
import math
from pygame.math import Vector2
from util import scale_img, blit_rotate_center

pygame.init()

GRASS = scale_img(pygame.image.load("img/grass.jpg"), 2.5)
TRACK = scale_img(pygame.image.load("img/track.png"), 0.9)
TRACK_BORDER = scale_img(pygame.image.load("img/track-border.png"),0.9)
FINISH = pygame.image.load("img/finish.png")

CAR = scale_img(pygame.image.load("img/red-car.png"), 0.55)

ZOOM = 1.5
WIDTH = 900
HEIGHT = 900

font = pygame.font.SysFont("Arial", 28)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Racist")

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG 
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

        self.gear = 1
        self.gear_ratio = {1 : 0.25, 2 : 0.45, 3 : 0.65, 4 : 0.85, 5 : 1.0}

    def gear_up(self):
        if self.gear < len(self.gear_ratio):
            self.gear += 1

    def gear_down(self):
        if self.gear > 1:
            self.gear -= 1
            

    def gear_max(self):
        return self.max_vel * self.gear_ratio[self.gear]


    def move_forward(self):
        gear_vel = self.gear_max()
        
        gear_accel = self.acceleration * (0.5 + self.gear * 0.2)
        self.vel = min(self.vel + gear_accel, gear_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
    
        self.y -= vertical
        self.x -= horizontal

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def draw(self, screen, camera_offset):
        draw_pos = (self.x - camera_offset.x, self.y - camera_offset.y)
        blit_rotate_center(screen, self.img, draw_pos, self.angle)

    def camera(self):
        screen_center = Vector2((WIDTH / ZOOM) / 2, (HEIGHT / ZOOM) / 2)
        car_center = Vector2(self.x + self.img.get_width() / 2, self.y + self.img.get_height() / 2)
        offset = car_center - screen_center 

        offset.x = max(0, min(offset.x, TRACK.get_width() - (WIDTH / ZOOM)))
        offset.y = max(0, min(offset.y, TRACK.get_height() - (HEIGHT / ZOOM)))

        return offset


class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = (180, 200)
    

def draw(screen, images, player_car):
    camera_offset = player_car.camera()
    world_surface = pygame.Surface((WIDTH / ZOOM, HEIGHT / ZOOM))

    for img, pos in images:
        
        world_surface.blit(img, (pos[0] - camera_offset.x, pos[1] - camera_offset.y))

    player_car.draw(world_surface, camera_offset)

    scaled = pygame.transform.scale(world_surface, (WIDTH, HEIGHT))
    screen.blit(scaled, (0, 0))

    gear_text = font.render(f"Gear: {player_car.gear}", True, (255, 255, 255))
    speed_text = font.render(f"Speed: {abs(player_car.vel):.1f}", True, (255, 255, 255))
    screen.blit(gear_text, (10, 10))
    screen.blit(speed_text, (10, 40))

    pygame.display.update()

running = True
FPS = 60
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0))]
player_car = PlayerCar(8, 4) 


while running:
    clock.tick(FPS)

    draw(screen, images, player_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                player_car.gear_up()
            if event.key == pygame.K_q:
                player_car.gear_down()
        

    keys = pygame.key.get_pressed()
    moved = False
    
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)

    
    if not moved:
        player_car.reduce_speed()
        
pygame.quit()

