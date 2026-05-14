import random


def _in_room(c, r, room):
    return room["x"] <= c < room["x"] + room["w"] and room["y"] <= r < room["y"] + room["h"]


def _mouth_tiles(carved, room):
    """Все клетки коридора снаружи комнаты, граничащие с её полом — полная ширина прохода."""
    ortho = ((0, 1), (0, -1), (1, 0), (-1, 0))
    seen = set()
    out = []
    for (c, r) in carved:
        if _in_room(c, r, room):
            continue
        for dc, dr in ortho:
            if _in_room(c + dc, r + dr, room):
                if (c, r) not in seen:
                    seen.add((c, r))
                    out.append((c, r))
                break
    return out


def create_corridor(game_map, x1, y1, x2, y2, carved_out=None):

    thickness = 4

    if random.random() > 0.5:
        # Горизонтально -> Вертикально
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for t in range(thickness):
                ty = y1 + t - thickness // 2  # Центрируем ширину относительно линии
                if 0 <= ty < len(game_map):
                    game_map[ty][x] = 0
                    if carved_out is not None:
                        carved_out.add((x, ty))

        for y in range(min(y1, y2), max(y1, y2) + 1):
            for t in range(thickness):
                tx = x2 + t - thickness // 2
                if 0 <= tx < len(game_map[0]):
                    game_map[y][tx] = 0
                    if carved_out is not None:
                        carved_out.add((tx, y))
    else:
        # Вертикально -> Горизонтально
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for t in range(thickness):
                tx = x1 + t - thickness // 2
                if 0 <= tx < len(game_map[0]):
                    game_map[y][tx] = 0
                    if carved_out is not None:
                        carved_out.add((tx, y))

        for x in range(min(x1, x2), max(x1, x2) + 1):
            for t in range(thickness):
                ty = y2 + t - thickness // 2
                if 0 <= ty < len(game_map):
                    game_map[ty][x] = 0
                    if carved_out is not None:
                        carved_out.add((x, ty))


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

        door_tiles = []
        # Соединяем с предыдущей комнатой
        if len(rooms) > 0:
            prev_room = rooms[-1]
            carved = set()
            create_corridor(game_map, prev_room["cx"], prev_room["cy"], cx, cy, carved)
            curr_room = {"x": x, "y": y, "w": w, "h": h, "cx": cx, "cy": cy}
            into_prev = _mouth_tiles(carved, prev_room)
            into_curr = _mouth_tiles(carved, curr_room)
            for t in into_prev:
                if t not in prev_room["door_tiles"]:
                    prev_room["door_tiles"].append(t)
            door_tiles = into_curr

        rooms.append({"cx": cx, "cy": cy, "x": x, "y": y, "w": w, "h": h, "door_tiles": door_tiles})

    # Возвращаем карту и центр самой первой комнаты для спавна игрока
    return game_map, rooms[0]["cx"], rooms[0]["cy"], rooms
