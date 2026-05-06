import pygame

def scale_img(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(screen, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft = top_left).center)
    screen.blit(rotated_image, new_rect.topleft)

def format_time(seconds):
    if seconds is None:
        return "--:--.--"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    return f"{mins:02d}:{secs:02d}.{centis:02d}"