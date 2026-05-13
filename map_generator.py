import random


def create_corridor(game_map, x1, y1, x2, y2):

    thickness = 4

    if random.random() > 0.5:
        # Горизонтально -> Вертикально
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for t in range(thickness):
                ty = y1 + t - thickness // 2  # Центрируем ширину относительно линии
                if 0 <= ty < len(game_map):
                    game_map[ty][x] = 0

        for y in range(min(y1, y2), max(y1, y2) + 1):
            for t in range(thickness):
                tx = x2 + t - thickness // 2
                if 0 <= tx < len(game_map[0]):
                    game_map[y][tx] = 0
    else:
        # Вертикально -> Горизонтально
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for t in range(thickness):
                tx = x1 + t - thickness // 2
                if 0 <= tx < len(game_map[0]):
                    game_map[y][tx] = 0

        for x in range(min(x1, x2), max(x1, x2) + 1):
            for t in range(thickness):
                ty = y2 + t - thickness // 2
                if 0 <= ty < len(game_map):
                    game_map[ty][x] = 0


def create_map(cols, rows, max_rooms=12):

    game_map = [[1 for _ in range(cols)] for _ in range(rows)]
    rooms = []

    # Делим карту на сетку (например, 4 колонки и 3 строки = 12 ячеек)
    grid_cols = 4
    grid_rows = 3
    cell_w = cols // grid_cols
    cell_h = rows // grid_rows

    for i in range(max_rooms):
        # Вычисляем текущую ячейку сетки
        grid_x = i % grid_cols
        grid_y = i // grid_cols

        # Размеры комнаты (не больше размера ячейки!)
        w = random.randint(12, 12)
        h = random.randint(12, 12)

        # Центрируем комнату внутри ячейки сетки
        # Это создает ту самую "ровную" структуру
        x = grid_x * cell_w + (cell_w - w) // 2
        y = grid_y * cell_h + (cell_h - h) // 2

        # Рисуем пол комнаты
        for r in range(y, y + h):
            for c in range(x, x + w):
                if 0 <= r < rows and 0 <= c < cols:
                    game_map[r][c] = 0

        cx, cy = x + w // 2, y + h // 2

        # Соединяем с предыдущей комнатой
        if len(rooms) > 0:
            prev_room = rooms[-1]
            create_corridor(game_map, prev_room['cx'], prev_room['cy'], cx, cy)

        rooms.append({'cx': cx, 'cy': cy})

    # Возвращаем карту и центр самой первой комнаты для спавна игрока
    return game_map, rooms[0]['cx'], rooms[0]['cy']