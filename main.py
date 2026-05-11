import pygame
from app.core.config import clock, FPS, images, screen, TRACK_BORDER_MASK
from app.car.player_car import player_car
from app.car.enemy_car import enemy_car
from app.display import draw

running = True

if __name__ == "__main__":
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
                    pygame.quit()
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
