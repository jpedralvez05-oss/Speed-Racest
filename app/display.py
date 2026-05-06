import pygame
from app.core import config
from app.core.util import format_time
from app.draw.speedometer import draw_speedometer
from app.draw.tachometer import draw_tachometer

def draw(screen, images, player_car, enemy_car, enemy_car_2):
    camera_offset = player_car.camera()
    world_surface = pygame.Surface((int(config.WIDTH / config.ZOOM), int(config.HEIGHT / config.ZOOM)))
    for img, pos in images:
        world_surface.blit(
            img, (pos[0] - camera_offset.x, pos[1] - camera_offset.y))
    world_surface.blit(config.FINISH, (config.FINISH_POS[0] - camera_offset.x,
                                config.FINISH_POS[1] - camera_offset.y))
    player_car.draw(world_surface, camera_offset)
    enemy_car.draw(world_surface, camera_offset)
    enemy_car_2.draw(world_surface, camera_offset)
    scaled = pygame.transform.scale(world_surface, (config.WIDTH, config.HEIGHT))
    screen.blit(scaled, (0, 0))
    # --- HUD ---
    if player_car.gear == -1:
        gear_display = "R"
    elif player_car.gear == 0:
        gear_display = "N"
    else:
        gear_display = str(player_car.gear)
    gear_text = config.font.render(f"Gear: {gear_display}", True, (255, 255, 255))
    speed_text = config.font.render(
        f"Speed: {abs(player_car.vel):.1f}", True, (255, 255, 255))
    rpm_text = config.font.render(
        f"RPM: {int(player_car.rpm * 100)}%", True, (255, 255, 255))
    # Lap timing HUD (top-right)
    lap_text = config.font.render(f"Lap: {player_car.lap}", True, (255, 255, 255))
    current_time_text = config.font.render(
        f"Time: {format_time(player_car.current_lap_time)}", True, (255, 255, 0))
    best_time_text = config.font.render(
        f"Best: {format_time(player_car.best_lap_time)}", True, (0, 220, 100))
    screen.blit(rpm_text, (10, 70))
    screen.blit(gear_text, (10, 10))
    screen.blit(speed_text, (10, 40))
    screen.blit(lap_text, (config.WIDTH - 160, 10))
    screen.blit(current_time_text, (config.WIDTH - 240, 40))
    screen.blit(best_time_text, (config.WIDTH - 240, 70))
    # Flash last lap time in the center for 3 seconds after completing a lap
    if player_car.last_lap_time is not None and player_car.finish_cooldown > 0:
        msg = config.font_large.render(
            f"Lap {player_car.lap}  {format_time(player_car.last_lap_time)}",
            True, (255, 220, 0))
        msg_rect = msg.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 60))
        screen.blit(msg, msg_rect)
    player_car.update_sound()
    draw_speedometer(screen, player_car)
    draw_tachometer(screen, player_car)
    pygame.display.update()