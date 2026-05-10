import pygame
import random
from app.core.config import WIDTH, ZOOM, HEIGHT, FINISH, FINISH_POS, enemy_path, font, font_large
from app.core.util import format_time
from app.draw.gauge import draw_gauge

def apply_scanlines(screen):
    width, height = screen.get_size()
    scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for y in range(0, height, 4):
        pygame.draw.line(scanline_surface, (0, 0, 0, 60), (0, y), (width, y))

    screen.blit(scanline_surface, (0, 0))

def add_glitch_effect(height, width, glitch_surface, intensity):
    shift_amount = {"minimum": 10, "medium": 15, "maximum": 40}.get(intensity, 20)
    if random.random() < 0.1:
        y_start = random.randint(0, height - 20)
        slice_height = random.randint(5, 20)
        offset = random.randint(-shift_amount, shift_amount)

        slice_area = pygame.Rect(0, y_start, width, slice_height)
        slice_copy = glitch_surface.subsurface(slice_area).copy()
        glitch_surface.blit(slice_copy, (offset, y_start))

def apply_glow(screen):
    width, height = screen.get_size()
    glow_surf = pygame.transform.smoothscale(screen, (width // 2, height // 2))
    glow_surf = pygame.transform.smoothscale(glow_surf, (width, height))
    glow_surf.set_alpha(100)
    screen.blit(glow_surf, (0, 0))

 
def draw(screen, images, player_car, enemy_car):
    camera_offset = player_car.camera()
    world_surface = pygame.Surface((int(WIDTH / ZOOM), int(HEIGHT / ZOOM)))
    for img, pos in images:
        world_surface.blit(
            img, (pos[0] - camera_offset.x, pos[1] - camera_offset.y))
    world_surface.blit(FINISH, (FINISH_POS[0] - camera_offset.x,
                                FINISH_POS[1] - camera_offset.y))
    player_car.draw(world_surface, camera_offset)
    enemy_car.draw(world_surface, camera_offset)
    scaled = pygame.transform.scale(world_surface, (WIDTH, HEIGHT))
    screen.blit(scaled, (0, 0))

    for point in enemy_path:
        pygame.draw.circle(world_surface, (255, 0, 0),
        (point[0] - camera_offset.x, point[1] - camera_offset.y), 5)
    
    # --- HUD ---
    if player_car.gear == -1:
        gear_display = "R"
    elif player_car.gear == 0:
        gear_display = "N"
    else:
        gear_display = str(player_car.gear)
    gear_text = font.render(f"Gear: {gear_display}", True, (255, 255, 255))
    speed_text = font.render(
        f"Speed: {abs(player_car.vel):.1f}", True, (255, 255, 255))
    rpm_text = font.render(
        f"RPM: {int(player_car.rpm * 100)}%", True, (255, 255, 255))
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
    draw_gauge(screen, player_car)
    apply_scanlines(screen)
    apply_glow(screen)
    add_glitch_effect(HEIGHT, WIDTH, screen, "medium")

    pygame.display.update()