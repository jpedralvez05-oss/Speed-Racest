import pygame
import os
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
GAUGE_IMG = pygame.transform.scale(
    pygame.image.load("app/img/Speedometer.png"), (370, 200))

ZOOM = 2.5
WIDTH = 1024
HEIGHT = 768

font = pygame.font.SysFont("Arial", 28)
font_large = pygame.font.SysFont("Arial", 42, bold=True)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Racest")
THUMBNAIL = pygame.transform.scale(pygame.image.load(
    "app/img/Game Thumbnail.jpg").convert(), (WIDTH, HEIGHT))

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
    (2181, 949),
    (2205, 973),
    (2229, 997),
    (2253, 1021),
    (2265, 1049),
    (2281, 1077),
    (2301, 1105),
    (2325, 1129),
    (2349, 1153),
    (2361, 1181),
    (2373, 1209),
    (2385, 1237),
    (2405, 1265),
    (2425, 1289),
    (2434, 1321),
    (2449, 1348),
    (2465, 1377),
    (2482, 1409),
    (2494, 1437),
    (2509, 1465),
    (2518, 1493),
    (2530, 1525),
    (2530, 1557),
    (2525, 1589),
    (2509, 1609),
    (2477, 1609),
    (2445, 1613),
    (2417, 1613),
    (2393, 1589),
    (2369, 1565),
    (2345, 1541),
    (2327, 1513),
    (2317, 1485),
    (2301, 1457),
    (2281, 1433),
    (2253, 1417),
    (2225, 1401),
    (2197, 1389),
    (2169, 1377),
    (2141, 1365),
    (2117, 1341),
    (2097, 1316),
    (2090, 1285),
    (2081, 1256),
    (2065, 1229),
    (2037, 1217),
    (2005, 1213),
    (1973, 1209),
    (1941, 1201),
    (1913, 1185),
    (1901, 1161),
    (1885, 1133),
    (1877, 1101),
    (1877, 1069),
    (1877, 1037),
    (1877, 1005),
    (1879, 973),
    (1879, 941),
    (1874, 909),
    (1853, 889),
    (1825, 873),
    (1797, 861),
    (1773, 837),
    (1741, 833),
    (1713, 821),
    (1685, 809),
    (1657, 809),
    (1633, 829),
    (1605, 841),
    (1577, 853),
    (1549, 865),
    (1521, 877),
    (1493, 889),
    (1465, 905),
    (1441, 929),
    (1421, 953),
    (1401, 977),
    (1377, 1005),
    (1353, 1025),
    (1325, 1041),
    (1293, 1047),
    (1261, 1047),
    (1233, 1057),
    (1205, 1045),
    (1181, 1021),
    (1157, 997),
    (1133, 973),
    (1109, 949),
    (1097, 920),
    (1113, 881),
    (1101, 853),
    (1093, 821),
    (1089, 789),
    (1089, 757),
    (1069, 733),
    (1049, 705),
    (1061, 677),
    (1065, 645),
    (1065, 613),
    (1065, 581),
    (1065, 549),
    (1065, 517),
    (1067, 485),
    (1085, 457),
    (1089, 425),
    (1065, 409),
    (1033, 401),
    (1021, 429),
    (1009, 457),
    (993, 485),
    (973, 509),
    (949, 529),
    (921, 545),
    (893, 557),
    (869, 581),
    (843, 605),
    (813, 617),
    (785, 629),
    (761, 649),
    (733, 637),
    (701, 629),
    (669, 625),
    (637, 613),
    (609, 601),
    (577, 601),
    (553, 581),
    (525, 561),
    (509, 537),
    (497, 509),
    (485, 481),
    (473, 453),
    (461, 425),
    (449, 397),
    (437, 369),
    (433, 341),
    (405, 325),
    (377, 313),
    (349, 301),
    (317, 301),
    (289, 289),
    (261, 273),
    (229, 281),
    (201, 297),
    (177, 321),
    (153, 345),
    (129, 369),
    (113, 397),
    (125, 425),
    (149, 449),
    (173, 473),
    (197, 497),
    (221, 521),
    (245, 545),
    (269, 569),
    (293, 593),
    (321, 613),
    (349, 625),
    (377, 641),
    (405, 653),
    (433, 665),
    (461, 677),
    (489, 689),
    (517, 705),
    (545, 717),
    (573, 729),
    (601, 741),
    (629, 753),
    (657, 765),
    (689, 773),
    (717, 785),
    (741, 805),
    (770, 817),
    (797, 829),
    (829, 841),
    (857, 853),
    (889, 857),
    (921, 857),
    (953, 861),
    (985, 861),
    (1017, 869),
    (1041, 893),
    (1069, 905),
    (1097, 920),
    (1120, 900),
    (1133, 901),
    (1161, 889),
    (1189, 877),
    (1221, 870),
    (1250, 861),
    (1277, 849),
    (1305, 838),
    (1331, 822),
    (1361, 811),
    (1391, 795),
    (1418, 773),
    (1445, 749),
    (1473, 725),
    (1497, 701),
    (1521, 677),
    (1545, 654),
    (1573, 633),
    (1601, 621),
    (1625, 645),
    (1649, 669),
    (1673, 689),
    (1705, 681),
    (1733, 665),
    (1765, 665),
    (1797, 657),
    (1829, 653),
    (1861, 653),
    (1889, 665),
    (1917, 681),
    (1941, 701),
    (1965, 725),
    (1989, 749),
    (2013, 773),
    (2037, 797),
    (2061, 821),
    (2085, 845),
    (2097, 873),
    (2113, 901),
    (2137, 925),
    (2165, 945),
    (2181, 949)
]

FPS = 60
clock = pygame.time.Clock()
images = [(BG, (0, 0)), (TRACK, (0, 0))]
