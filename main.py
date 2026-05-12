import pygame
import sys
from app.core.config import clock, FPS, images, screen, TRACK_BORDER_MASK, THUMBNAIL, WIDTH, HEIGHT, font_large
from app.car.player_car import player_car
from app.car.enemy_car import enemy_car
from app.display import draw

def main_menu():
    menu_running = True
    
    # buttonss
    button_width = 200
    button_height = 60
    border_radius = 15 
    
    play_button = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 - 50, button_width, button_height)
    quit_button = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50, button_width, button_height)

    while menu_running:
        screen.blit(THUMBNAIL, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
    
        if play_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (185, 185, 185), play_button, border_radius=border_radius) 
        else:
            pygame.draw.rect(screen, (255, 255, 255), play_button, border_radius=border_radius)
            
        play_text = font_large.render("PLAY", True, (0, 0, 0))
        screen.blit(play_text, (play_button.centerx - play_text.get_width() // 2, play_button.centery - play_text.get_height() // 2))

        if quit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (185, 185, 185), quit_button, border_radius=border_radius)
        else:
            pygame.draw.rect(screen, (255, 255, 255), quit_button, border_radius=border_radius)
            
        quit_text = font_large.render("QUIT", True, (0, 0, 0))
        screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, quit_button.centery - quit_text.get_height() // 2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if play_button.collidepoint(mouse_pos):
                        return
                    if quit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

        pygame.display.update()
        clock.tick(FPS)

running = True

if __name__ == "__main__":
    main_menu()

    while running:
        clock.tick(FPS)
        player_car.update_lap()
        enemy_car.move_enemy(player_car)
        draw(screen, images, player_car, enemy_car)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                camera_offset = player_car.camera()
                # Calculate true world coordinates
                real_x = int(pos[0] + camera_offset.x)
                real_y = int(pos[1] + camera_offset.y)
                print(f"({real_x}, {real_y}),")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    player_car.gear_up()
                if event.key == pygame.K_k:
                    player_car.gear_down()
                if event.key == pygame.K_r:
                    player_car.reset_pos()
                    player_car.reset_time()
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    player_car.reset_pos()


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
    sys.exit()