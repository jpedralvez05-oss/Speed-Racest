from app.core.config import HEIGHT, GAUGE_IMG
from app.car.rpm_angle import get_rpm_angle
from app.car.speed_angle import get_speed_angle
from app.draw.needle import draw_needle

def draw_gauge(screen, player_car):
    gauge_x = 20
    gauge_y = HEIGHT - 220
    gauge_img_y = gauge_y - 115

    screen.blit(GAUGE_IMG, (gauge_x, gauge_img_y))

    tach_center = (gauge_x + 100, gauge_y + 120)  
    speed_center = (gauge_x + 240, gauge_y + 150) 

    # --- Angles ---
    rpm_angle = get_rpm_angle(player_car)
    speed_angle = get_speed_angle(player_car)

    # --- Draw needles ---
    draw_needle(screen, tach_center, rpm_angle, 30)
    draw_needle(screen, speed_center, speed_angle, 60)
