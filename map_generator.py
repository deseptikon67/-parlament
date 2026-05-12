import random

def create_map(cols, rows):
    game_map = [[0 for _ in range(cols)] for _ in range(rows)]
    center_x = cols // 2
    center_y = rows // 2
    for r in range(rows):
        for c in range(cols):
            if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                game_map[r][c] = 1
            else:
                is_far_from_center = abs(c - center_x) > 1 or abs(r - center_y) > 1
                if is_far_from_center:
                    if random.random() < 0.15:  # 15% шанс появления случайной стены
                        game_map[r][c] = 1

            spawn_x = center_x
            spawn_y = center_y

    return game_map, spawn_x, spawn_y