import random

import pygame

import sprites
from enemies import BurstRangedEnemy, MeleeEnemy, RangedEnemy


class Room:
    def __init__(self, room_data, tile_size):
        self.tile_size = tile_size
        self.cx = room_data["cx"]
        self.cy = room_data["cy"]
        self.pixel_rect = pygame.Rect(
            room_data["x"] * tile_size,
            room_data["y"] * tile_size,
            room_data["w"] * tile_size,
            room_data["h"] * tile_size,
        )
        self.door_tiles = list(room_data.get("door_tiles") or [])
        self.cleared = False
        self.activated = False
        self.room_enemies = []
        self.corridor_walls = []

    def is_player_near_room_center(self, player_rect):
        """Активация примерно от центра комнаты: пересечение с центральной половиной площади."""
        zw = max(self.tile_size, int(self.pixel_rect.width * 0.5))
        zh = max(self.tile_size, int(self.pixel_rect.height * 0.5))
        zone = pygame.Rect(0, 0, zw, zh)
        zone.center = self.pixel_rect.center
        return zone.colliderect(player_rect)

    def _pick_enemy(self, px, py):
        r = random.random()
        if r < 0.12:
            return BurstRangedEnemy(px, py)
        if r < 0.56:
            return MeleeEnemy(px, py)
        return RangedEnemy(px, py)

    def activate(self, enemies_group, all_sprites, walls_group, doors_group):
        if self.activated:
            return
        self.activated = True
        ts = self.tile_size
        margin = 2 * ts
        count = random.randint(1, 4)
        for _ in range(count):
            px = random.randint(self.pixel_rect.left + margin, self.pixel_rect.right - margin - ts)
            py = random.randint(self.pixel_rect.top + margin, self.pixel_rect.bottom - margin - ts)
            e = self._pick_enemy(px, py)
            enemies_group.add(e)
            all_sprites.add(e)
            self.room_enemies.append(e)
        seen = set()
        for c, r in self.door_tiles:
            if (c, r) in seen:
                continue
            seen.add((c, r))
            wall = sprites.Wall(c * ts, r * ts)
            walls_group.add(wall)
            all_sprites.add(wall)
            self.corridor_walls.append(wall)

    def check_cleared(self):
        if not self.activated or self.cleared:
            return False
        if all(not e.alive() for e in self.room_enemies):
            self.cleared = True
            for w in self.corridor_walls:
                w.kill()
            self.corridor_walls.clear()
            return True
        return False


class RoomManager:
    def __init__(self, rooms_data, tile_size):
        self.rooms = [Room(r, tile_size) for r in rooms_data[1:]]
        self.card_event_pending = False
        self.room_just_cleared = False

    def update(self, player, enemies_group, all_sprites, walls_group, doors_group):
        self.room_just_cleared = False
        for room in self.rooms:
            if not room.activated and room.is_player_near_room_center(player.rect):
                room.activate(enemies_group, all_sprites, walls_group, doors_group)
            if room.activated and not room.cleared:
                if room.check_cleared():
                    self.room_just_cleared = True
                    has_uncleared = any(not r.cleared for r in self.rooms)
                    if has_uncleared:
                        self.card_event_pending = True
