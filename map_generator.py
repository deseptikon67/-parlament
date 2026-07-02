import random


def _in_room(c, r, room):
    return (
        room["x"] <= c < room["x"] + room["w"]
        and room["y"] <= r < room["y"] + room["h"]
    )


def _mouth_tiles(carved, room):
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
    path_type = random.choice(["horizontal", "vertical"])
    order = []

    if path_type == "horizontal":
        for row in range(grid_rows):
            cols_range = (
                range(grid_cols)
                if row % 2 == 0
                else range(grid_cols - 1, -1, -1)
            )
            for col in cols_range:
                order.append((col, row))
    else:
        for col in range(grid_cols):
            rows_range = (
                range(grid_rows)
                if col % 2 == 0
                else range(grid_rows - 1, -1, -1)
            )
            for row in rows_range:
                order.append((col, row))

    if random.choice([True, False]):
        order.reverse()

    return order[:max_rooms]


def create_map(cols, rows, max_rooms=6):
    """Генерирует карту Soul Knight, возвращая точные раздельные координаты для

    игрока и лифта.
    """
    game_map = [[1 for _ in range(cols)] for _ in range(rows)]
    rooms = []

    if random.choice([True, False]):
        grid_cols, grid_rows = 3, 2
    else:
        grid_cols, grid_rows = 2, 3

    cell_w = cols // grid_cols
    cell_h = rows // grid_rows

    order = _snake_order(grid_cols, grid_rows, max_rooms)

    for grid_x, grid_y in order:
        max_w = max(8, cell_w - 4)
        min_w = max(6, int(cell_w * 0.70))
        w = random.randint(min(min_w, max_w), max_w)

        max_h = max(8, cell_h - 4)
        min_h = max(6, int(cell_h * 0.70))
        h = random.randint(min(min_h, max_h), max_h)

        cx = grid_x * cell_w + cell_w // 2
        cy = grid_y * cell_h + cell_h // 2

        x = cx - w // 2
        y = cy - h // 2

        if len(rooms) == 0 or len(rooms) == len(order) - 1:
            room_style = "rectangle"
        else:
            room_style = random.choice(["rectangle", "octagon", "columns"])

        for r in range(y, y + h):
            for c in range(x, x + w):
                if 0 <= r < rows and 0 <= c < cols:
                    if room_style == "octagon":
                        shave = max(1, min(3, w // 4, h // 4))
                        if (c - x) + (r - y) < shave:
                            continue
                        if ((x + w - 1) - c) + (r - y) < shave:
                            continue
                        if (c - x) + ((y + h - 1) - r) < shave:
                            continue
                        if ((x + w - 1) - c) + ((y + h - 1) - r) < shave:
                            continue
                    elif room_style == "columns":
                        if (c < x + 2 or c >= x + w - 2) and (
                            r < y + 2 or r >= y + h - 2
                        ):
                            continue

                    game_map[r][c] = 0

        door_tiles = []
        if len(rooms) > 0:
            prev_room = rooms[-1]
            carved = set()
            thickness = 3
            x1, y1 = prev_room["cx"], prev_room["cy"]
            x2, y2 = cx, cy

            if x1 == x2:
                for ty in range(min(y1, y2), max(y1, y2) + 1):
                    for t in range(-thickness // 2, thickness // 2 + 1):
                        tx = x1 + t
                        if 0 <= ty < rows and 0 <= tx < cols:
                            game_map[ty][tx] = 0
                            carved.add((tx, ty))
            else:
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
                "is_treasure": False,
                "is_shop": False,
                "type": "combat",
            }
        )

    # НАСТРОЙКА РОЛЕЙ
    if len(rooms) >= 2:
        rooms[0]["is_spawn"] = True
        rooms[0]["type"] = "spawn"

        rooms[-1]["is_exit"] = True
        rooms[-1]["type"] = "exit"

        if len(rooms) >= 4:
            rooms[1]["is_treasure"] = True
            rooms[1]["type"] = "treasure"
            rooms[2]["is_shop"] = True
            rooms[2]["type"] = "shop"

    # Возвращаем карту, координаты СТАРТА (индекс 0) и координаты ВЫХОДА (индекс -1)
    return (
        game_map,
        rooms[0]["cx"],
        rooms[0]["cy"],
        rooms[-1]["cx"],
        rooms[-1]["cy"],
        rooms,
    )