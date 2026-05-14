# -parlament

**Список изменений (body):**

- **Игрок (`sprites.py`):** HP, неуязвимость, урон `take_damage`, стрельба очередями по стрелкам, движение по физическим WASD (`get_scancode_pressed` / KSCAN), коллизии со стенами без смены логики осей.
- **Пули:** `PlayerBullet` и `EnemyBullet` в `enemies.py`, коллизии со стенами и границей карты.
- **Враги (`enemies.py`):** базовый `Enemy`, `MeleeEnemy`, `RangedEnemy`, `BurstRangedEnemy` (очередь из 3 пуль), движение `_move_towards`, полоска HP, коллизии враг ↔ враг (`resolve_peer_collisions`).
- **Комнаты (`room_manager.py`, `map_generator.py`):** данные комнат с `x,y,w,h` и `door_tiles`; устья коридоров с обеих сторон; активация при входе в центральную зону комнаты; при активации — враги и стены из `sprites.Wall` по всем клеткам устья; снятие стен после зачистки.
- **UI (`hud.py`):** полоска HP игрока, `PauseMenu`, `DeathMenu`.
- **`main.py`:** игровой цикл, группы спрайтов, `RoomManager`, пауза по Esc, коллизии пуль/врагов, камера из `settings`.
- **`map_generator.py`:** возврат списка `rooms` и расширенный `rooms.append` (без лишних правок генерации, кроме нужных под комнаты/коридоры).

---
