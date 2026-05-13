import random


def create_corridor(game_map, x1, y1, x2, y2):
    thickness = 2 # Ширина коридора
    # Горизонтальный проход
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for t in range(thickness):
            if y1 + t < len(game_map):
                game_map[y1 + t][x] = 0
    # Вертикальный проход
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for t in range(thickness):
            if x2 + t < len(game_map[0]):
                game_map[y][x2 + t] = 0


import random


def create_map(cols, rows, max_rooms=15):
    game_map = [[1 for _ in range(cols)] for _ in range(rows)]
    rooms = []
    padding = 2

    # Пробуем создать max_rooms комнат
    for i in range(max_rooms * 5):
        if len(rooms) >= max_rooms:
            break

        # 1. ПЕРВАЯ КОМНАТА: ставим строго в центр
        if len(rooms) == 0:
            w, h = 5, 5  # Маленькая стартовая комната
            x = cols // 2 - w // 2
            y = rows // 2 - h // 2
        else:
            # ОСТАЛЬНЫЕ КОМНАТЫ: случайный размер и позиция
            w = random.randint(6, 12)
            h = random.randint(6, 12)

            # Защита от вылета (убедимся, что диапазон положительный)
            max_x = cols - w - padding
            max_y = rows - h - padding
            if max_x <= padding or max_y <= padding:
                continue

            x = random.randint(padding, max_x)
            y = random.randint(padding, max_y)

        # 2. Проверка на пересечение
        new_room = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h}
        check_rect = {
            'x1': x - padding, 'y1': y - padding,
            'x2': x + w + padding, 'y2': y + h + padding
        }

        intersects = False
        for other in rooms:
            if (check_rect['x1'] <= other['x2'] and check_rect['x2'] >= other['x1'] and
                    check_rect['y1'] <= other['y2'] and check_rect['y2'] >= other['y1']):
                intersects = True
                break

        if not intersects:
            # Рисуем пол
            for r in range(y, y + h):
                for c in range(x, x + w):
                    game_map[r][c] = 0

            cx, cy = x + w // 2, y + h // 2

            # 3. Соединяем коридором
            if len(rooms) > 0:
                prev_room = rooms[-1]
                create_corridor(game_map, prev_room['cx'], prev_room['cy'], cx, cy)

            rooms.append({
                'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h,
                'cx': cx, 'cy': cy
            })

    # Игрок появляется в центре первой комнаты (которая теперь в центре карты)
    spawn_x, spawn_y = rooms[0]['cx'], rooms[0]['cy']
    return game_map, spawn_x, spawn_y