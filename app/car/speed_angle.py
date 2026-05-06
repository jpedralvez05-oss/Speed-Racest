import math

def get_speed_angle(player_car):
    speed = abs(player_car.vel)
    max_speed = player_car.max_vel

    ratio = min(speed / max_speed, 1)

    # Map 0 → 180°  and 1 → 0°
    return math.radians(180 - (ratio * 180))