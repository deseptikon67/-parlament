import random


def _in_room(c, r, room):
    return (
        room["x"] <= c < room["x"] + room["w"]
        and room["y"] <= r < room["y"] + room["h"]
    )


def _mouth_tiles(carved, room):
    """Все клетки коридора снаружи комнаты, граничащие с её полом."""
    ortho = ((0, 1), (0, -1), (1, 0), (-1, 0))
    seen = set()
    out = []
    for c, r in carved:
        if _in_room(c, r, room):
            continue
        for dc, dr in ortho:
            if _in_room(c + dc, r + dr, room):
                if (c, r) not in seen:
                    seen.add((c, r))
                    out.append((c, r))
                break
    return out


def _snake_order(grid_cols, grid_rows, max_rooms):
    order = []
    for row in range(grid_rows):
        cols_range = (
            range(grid_cols) if row % 2 == 0 else range(grid_cols - 1, -1, -1)
        )
        for col in cols_range:
            order.append((col, row))
            if len(order) >= max_rooms:
                return order
    return order


def create_map(cols, rows, max_rooms=6):
    """Генерирует карту этажа с ровными коридорами и безопасными зонами."""
    game_map = [[1 for _ in range(cols)] for _ in range(rows)]
    rooms = []

    # Сетка 3x2 для ~6 комнат
    grid_cols = 3
    grid_rows = 2
    cell_w = cols // grid_cols
    cell_h = rows // grid_rows

    order = _snake_order(grid_cols, grid_rows, max_rooms)

    for grid_x, grid_y in order:
        # Увеличенный размер комнат, как ты и просил
        w = random.randint(14, 18)
        h = random.randint(14, 18)

        # Вычисляем центр ячейки сетки
        cx = grid_x * cell_w + cell_w // 2
        cy = grid_y * cell_h + cell_h // 2

        # !!! ВОТ ЭТИ ДВЕ СТРОЧКИ БЫЛИ УТЕРЯНЫ !!!
        # Они переводят центр комнаты в координаты верхнего левого угла (x, y)
        x = cx - w // 2
        y = cy - h // 2

        # Теперь вырезание комнаты сработает без ошибок
        for r in range(y, y + h):
            for c in range(x, x + w):
                if 0 <= r < rows and 0 <= c < cols:
                    game_map[r][c] = 0

        door_tiles = []
        if len(rooms) > 0:
            prev_room = rooms[-1]
            carved = set()

            thickness = 3  # Ширина коридоров
            x1, y1 = prev_room["cx"], prev_room["cy"]
            x2, y2 = cx, cy

            if x1 == x2:  # Вертикальный коридор
                for ty in range(min(y1, y2), max(y1, y2) + 1):
                    for t in range(-thickness // 2, thickness // 2 + 1):
                        tx = x1 + t
                        if 0 <= ty < rows and 0 <= tx < cols:
                            game_map[ty][tx] = 0
                            carved.add((tx, ty))
            else:  # Горизонтальный коридор
                for tx in range(min(x1, x2), max(x1, x2) + 1):
                    for t in range(-thickness // 2, thickness // 2 + 1):
                        ty = y1 + t
                        if 0 <= ty < rows and 0 <= tx < cols:
                            game_map[ty][tx] = 0
                            carved.add((tx, ty))

            curr_room = {"x": x, "y": y, "w": w, "h": h, "cx": cx, "cy": cy}
            into_prev = _mouth_tiles(carved, prev_room)
            into_curr = _mouth_tiles(carved, curr_room)

            for t in into_prev:
                if t not in prev_room["door_tiles"]:
                    prev_room["door_tiles"].append(t)
            door_tiles = into_curr

        rooms.append(
            {
                "cx": cx,
                "cy": cy,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "door_tiles": door_tiles,
                "is_spawn": False,
                "is_exit": False,
            }
        )

    if rooms:
        rooms[0]["is_spawn"] = True
        rooms[-1]["is_exit"] = True

    return game_map, rooms[0]["cx"], rooms[0]["cy"], rooms