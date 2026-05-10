import math

def get_rpm_angle(player_car):
    rpm_ratio = player_car.rpm  # 0 → 1

    start_angle = 280  
    end_angle = 75  

    angle = start_angle + (end_angle - start_angle) * rpm_ratio
    return math.radians(angle)