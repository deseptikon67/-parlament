import pygame
import settings


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.x, self.y = float(x), float(y)
        self.vel_x, self.vel_y = dx * 7, dy * 7
        self.damage = damage

    def update(self, walls):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if pygame.sprite.spritecollide(self, walls, False):
            self.kill()
        map_w = settings.MAP_COLS * settings.TILE_SIZE
        map_h = settings.MAP_ROWS * settings.TILE_SIZE
        if not (0 <= self.x <= map_w):
            self.kill()
        if not (0 <= self.y <= map_h):
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.x, self.y = float(x), float(y)
        self.vel_x = dx * 4
        self.vel_y = dy * 4
        self.damage = damage

    def update(self, walls):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if pygame.sprite.spritecollide(self, walls, False):
            self.kill()
        map_w = settings.MAP_COLS * settings.TILE_SIZE
        map_h = settings.MAP_ROWS * settings.TILE_SIZE
        if not (0 <= self.x <= map_w):
            self.kill()
        if not (0 <= self.y <= map_h):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, speed, damage):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE - 10, settings.TILE_SIZE - 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = float(x)
        self.y = float(y)
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.last_attack = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw_health_bar(self, surface, camera):
        if self.hp >= self.max_hp:
            return
        bar_w = settings.TILE_SIZE - 10
        bar_h = 6
        draw_pos = camera.apply(self.rect)
        bx = draw_pos.x
        by = draw_pos.y - 10
        ratio = self.hp / self.max_hp
        color = (0, 200, 0) if ratio > 0.6 else (220, 200, 0) if ratio > 0.3 else (200, 0, 0)
        pygame.draw.rect(surface, (80, 80, 80), (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, color, (bx, by, int(bar_w * ratio), bar_h))

    def _move_towards(self, tx, ty, walls):
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        self.x += (dx / dist) * self.speed
        self.rect.x = int(self.x)
        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if dx > 0:
                self.rect.right = wall.rect.left
            else:
                self.rect.left = wall.rect.right
        self.x = float(self.rect.x)

        self.y += (dy / dist) * self.speed
        self.rect.y = int(self.y)
        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if dy > 0:
                self.rect.bottom = wall.rect.top
            else:
                self.rect.top = wall.rect.bottom
        self.y = float(self.rect.y)

    def resolve_peer_collisions(self, enemies):
        for other in pygame.sprite.spritecollide(self, enemies, False):
            if other is self:
                continue
            if not self.rect.colliderect(other.rect):
                continue
            overlap_x = min(self.rect.right, other.rect.right) - max(self.rect.left, other.rect.left)
            overlap_y = min(self.rect.bottom, other.rect.bottom) - max(self.rect.top, other.rect.top)
            if overlap_x < overlap_y:
                if self.rect.centerx < other.rect.centerx:
                    self.rect.right = other.rect.left
                else:
                    self.rect.left = other.rect.right
            else:
                if self.rect.centery < other.rect.centery:
                    self.rect.bottom = other.rect.top
                else:
                    self.rect.top = other.rect.bottom
            self.x = float(self.rect.x)
            self.y = float(self.rect.y)


class MeleeEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 3.5, 15)
        self.image.fill((200, 50, 50))
        self.agro_radius = 250
        self.attack_range = 50
        self.attack_cooldown = 1000

    def update(self, player, walls, enemy_bullets):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < self.agro_radius:
            self._move_towards(player.rect.centerx, player.rect.centery, walls)
        if dist < self.attack_range:
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.attack_cooldown:
                player.take_damage(self.damage)
                self.last_attack = now


class RangedEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 1.5, 10)
        self.image.fill((150, 50, 200))
        self.agro_radius = 350
        self.preferred_dist = 200
        self.shoot_cooldown = 1500

    def update(self, player, walls, enemy_bullets):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        if dist < self.agro_radius:
            if dist > self.preferred_dist:
                self._move_towards(player.rect.centerx, player.rect.centery, walls)
            elif dist < self.preferred_dist - 40:
                self._move_towards(self.rect.centerx - dx, self.rect.centery - dy, walls)
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.shoot_cooldown:
                ndx, ndy = dx / dist, dy / dist
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery, ndx, ndy, self.damage)
                enemy_bullets.add(bullet)
                self.last_attack = now


class BurstRangedEnemy(Enemy):
    """Редкий враг: очередь из трёх пуль с паузой между выстрелами."""

    def __init__(self, x, y):
        super().__init__(x, y, 45, 1.3, 8)
        self.image.fill((80, 40, 160))
        self.agro_radius = 340
        self.preferred_dist = 190
        self.burst_cooldown = 2600
        self.burst_interval_ms = 95
        self._burst_remaining = 0
        self._next_burst_shot = 0
        self.last_attack = pygame.time.get_ticks()

    def update(self, player, walls, enemy_bullets):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        if dist < self.agro_radius:
            if dist > self.preferred_dist:
                self._move_towards(player.rect.centerx, player.rect.centery, walls)
            elif dist < self.preferred_dist - 40:
                self._move_towards(self.rect.centerx - dx, self.rect.centery - dy, walls)

        now = pygame.time.get_ticks()
        ndx, ndy = dx / dist, dy / dist

        if self._burst_remaining > 0:
            if now >= self._next_burst_shot:
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery, ndx, ndy, self.damage)
                enemy_bullets.add(bullet)
                self._burst_remaining -= 1
                if self._burst_remaining > 0:
                    self._next_burst_shot = now + self.burst_interval_ms
                else:
                    self.last_attack = now
        elif dist < self.agro_radius and now - self.last_attack > self.burst_cooldown:
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, ndx, ndy, self.damage)
            enemy_bullets.add(bullet)
            self._burst_remaining = 2
            self._next_burst_shot = now + self.burst_interval_ms
