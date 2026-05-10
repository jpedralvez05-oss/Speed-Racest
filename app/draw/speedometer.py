from app.core import config
import pygame, math

def draw_speedometer(screen, player_car):
    center_x = 120
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
    speed = abs(player_car.vel)
    max_speed = player_car.max_vel
    speed_ratio = min(speed / max_speed, 1)
    angle = math.radians(180 - (speed_ratio * 180))
    needle_length = radius - 20
    needle_x = center_x + math.cos(angle) * needle_length
    needle_y = center_y - math.sin(angle) * needle_length
    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y),
                     (needle_x, needle_y), 4)
    pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 5)
    speed_text = config.font.render(f"{int(speed * 20)} km/h", True, (255, 255, 255))
    text_rect = speed_text.get_rect(center=(center_x, center_y + 40))
    screen.blit(speed_text, text_rect)