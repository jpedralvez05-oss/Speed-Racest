import pygame, os
from app.core.util import scale_img

pygame.init()
pygame.mixer.init()

BG = scale_img(pygame.image.load("app/img/background.png"), 0.9)
TRACK = scale_img(pygame.image.load("app/img/track.png"), 0.9)
TRACK_BORDER = scale_img(pygame.image.load("app/img/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = scale_img(pygame.transform.rotate(
    pygame.image.load("app/img/finish.png"), 45), 0.3)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (2180, 950)
CAR = scale_img(pygame.image.load("app/img/red-car.png"), 0.20)

ENEMY_CAR = scale_img(pygame.image.load("app/img/blue-car.png"), 0.20)
ENEMY_CAR_2 = scale_img(pygame.image.load("app/img/green-car.png"), 0.20)

ZOOM = 2
WIDTH = 1200
HEIGHT = 700

font = pygame.font.SysFont("Arial", 28)
font_large = pygame.font.SysFont("Arial", 42, bold=True)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Racest")

GEAR_DOWN_PATH = os.path.join('app/sounds', 'gear_down.mp3')
GEAR_UP_PATH = os.path.join('app/sounds', 'gear_up.mp3')
IDLE_PATH = os.path.join('app/sounds', 'idle.mp3')

first_gear_sound = os.path.join('app/sounds/accelerate', 'first_gear.mp3')
second_gear_sound = os.path.join('app/sounds/accelerate', 'second_gear.mp3')
third_gear_sound = os.path.join('app/sounds/accelerate', 'third_gear.mp3')
fourth_gear_sound = os.path.join('app/sounds/accelerate', 'fourth_gear.mp3')
fifth_gear_sound = os.path.join('app/sounds/accelerate', 'fifth_gear.mp3')

gear_down_sound = pygame.mixer.Sound(GEAR_DOWN_PATH)
gear_up_sound = pygame.mixer.Sound(GEAR_UP_PATH)
idle_sound = pygame.mixer.Sound(IDLE_PATH)
first_gear_play = pygame.mixer.Sound(first_gear_sound)
second_gear_play = pygame.mixer.Sound(second_gear_sound)
third_gear_play = pygame.mixer.Sound(third_gear_sound)
fourth_gear_play = pygame.mixer.Sound(fourth_gear_sound)
fifth_gear_play = pygame.mixer.Sound(fifth_gear_sound)

enemy_path = [
    (2100, 800),  
    (2180, 950), 
    (2208, 806),  
    (2060, 891),
    (1930, 804),
    (1413, 603),
    (1300, 615),
    (1126, 850),
    (948, 823),
    (683, 511),
    (318, 561)
    
]


enemy_path_2 = [
    (2100, 900),  
    (2180, 980),  
    (2238, 836),  
    (2090, 921),
    (1960, 834),
    (1443, 633),
    (1330, 645),
    (1156, 880),
    (978, 853),
    (713, 541),
    (348, 591)
]

FPS = 60
clock = pygame.time.Clock()
images = [(BG, (0, 0)), (TRACK, (0, 0))]