import math, pygame
from app.core import config

def draw_tachometer(screen, player_car):
    # bottom-left
    center_x = 320
    center_y = config.HEIGHT - 120
    radius = 90
    pygame.draw.circle(screen, (30, 30, 30), (center_x, center_y), radius)
    pygame.draw.circle(screen, (255, 255, 255),
                       (center_x, center_y), radius, 3)
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
    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y),
                     (needle_x, needle_y), 4)
    pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 5)
    rpm_value = int(rpm_ratio * 8000)
    rpm_text = config.font.render(f"{rpm_value} RPM", True, (255, 255, 255))
    text_rect = rpm_text.get_rect(center=(center_x, center_y + 40))
    screen.blit(rpm_text, text_rect)