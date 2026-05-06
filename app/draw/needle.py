import pygame, math

def draw_needle(screen, center, angle, length, color=(255, 0, 0)):
    end_x = center[0] + math.cos(angle) * length
    end_y = center[1] - math.sin(angle) * length
    pygame.draw.line(screen, color, center, (end_x, end_y), 4)
    pygame.draw.circle(screen, color, center, 5)