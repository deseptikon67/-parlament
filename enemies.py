import random
import math
import os
import pygame

import sprites
import settings

class PlayerBullet(pygame.sprite.Sprite):
    _BASE_IMAGE = None 

    def __init__(self, x, y, dx, dy, damage):
        super().__init__()
        
        self.x, self.y = float(x), float(y)
        self.vel_x, self.vel_y = dx * 7, dy * 7
        self.damage = damage
        
        if PlayerBullet._BASE_IMAGE is None:
            path = os.path.join("assets", "player_bullet.png")
            try:
                raw_img = pygame.image.load(path).convert_alpha()
                PlayerBullet._BASE_IMAGE = pygame.transform.scale(raw_img, (30, 30))
            except FileNotFoundError:
                fallback = pygame.Surface((15, 15)) 
                fallback.fill((255, 255, 0))
                PlayerBullet._BASE_IMAGE = fallback
                
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(PlayerBullet._BASE_IMAGE, angle)
            
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, walls):
        self.x += self.vel_x
        self.y += self.vel_y
        
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        if pygame.sprite.spritecollide(self, walls, False):
            self.kill()
            
        map_w = settings.MAP_COLS * settings.TILE_SIZE
        map_h = settings.MAP_ROWS * settings.TILE_SIZE
        
        if not (0 <= self.x <= map_w):
            self.kill()
        if not (0 <= self.y <= map_h):
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    _BASE_IMAGES = {}

    def __init__(self, x, y, dx, dy, damage, bullet_type="green"):
        super().__init__()
        
        self.x, self.y = float(x), float(y)
        self.vel_x = dx * 4
        self.vel_y = dy * 4
        self.damage = damage

        if bullet_type not in EnemyBullet._BASE_IMAGES:
            filename = "slime_bullet.png" if bullet_type == "green" else "purple_slime_bullet.png"
            fallback_color = (100, 255, 100) if bullet_type == "green" else (160, 40, 200)
            
            path = os.path.join("assets", filename)
            try:
                raw_img = pygame.image.load(path).convert_alpha()
                # Сначала масштабируем до желаемого визуального размера
                scaled_img = pygame.transform.scale(raw_img, (25, 25)) 
                
                # ВАЖНО: Обрезаем прозрачные края, чтобы хитбокс был tight (плотным)
                # get_bounding_rect() находит минимальный прямоугольник, содержащий все непрозрачные пиксели
                clip_rect = scaled_img.get_bounding_rect()
                final_img = scaled_img.subsurface(clip_rect)
                
                EnemyBullet._BASE_IMAGES[bullet_type] = final_img
                
            except FileNotFoundError:
                fallback = pygame.Surface((15, 15))
                fallback.fill(fallback_color)
                EnemyBullet._BASE_IMAGES[bullet_type] = fallback

        angle = math.degrees(math.atan2(-dy, dx))
        # При вращении снова могут появиться прозрачные углы, но subsurface уже убрал лишнее изначально
        self.image = pygame.transform.rotate(EnemyBullet._BASE_IMAGES[bullet_type], angle)
        
        self.rect = self.image.get_rect(center=(x, y))
        shrink_factor = 0.6 
        new_width = int(self.rect.width * shrink_factor)
        new_height = int(self.rect.height * shrink_factor)
        
        center_pos = self.rect.center
        self.rect.width = new_width
        self.rect.height = new_height
        self.rect.center = center_pos

    def update(self, walls):
        # ... ваш код update без изменений ...
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
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
        
        self.hitbox = pygame.Rect(0, 0, settings.TILE_SIZE - 15, settings.TILE_SIZE - 15)
        self.hitbox.x = x
        self.hitbox.y = y
        self.x = float(self.hitbox.x)
        self.y = float(self.hitbox.y)
        
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.last_attack = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def draw_health_bar(self, surface, camera):
        if self.hp >= self.max_hp:
            return
        bar_w = settings.TILE_SIZE - 10
        bar_h = 6
        draw_pos = camera.apply(self.hitbox)
        bx = draw_pos.x
        by = draw_pos.y - 15
        ratio = self.hp / self.max_hp
        color = (0, 200, 0) if ratio > 0.6 else (220, 200, 0) if ratio > 0.3 else (200, 0, 0)
        pygame.draw.rect(surface, (80, 80, 80), (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, color, (bx, by, int(bar_w * ratio), bar_h))

    def _move_towards(self, tx, ty, walls):
        dx = tx - self.hitbox.centerx
        dy = ty - self.hitbox.centery
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        self.x += (dx / dist) * self.speed
        self.hitbox.x = int(self.x)
        for wall in walls:
            if self.hitbox.colliderect(wall.rect):
                if dx > 0:
                    self.hitbox.right = wall.rect.left
                else:
                    self.hitbox.left = wall.rect.right
        self.x = float(self.hitbox.x)

        self.y += (dy / dist) * self.speed
        self.hitbox.y = int(self.y)
        for wall in walls:
            if self.hitbox.colliderect(wall.rect):
                if dy > 0:
                    self.hitbox.bottom = wall.rect.top
                else:
                    self.hitbox.top = wall.rect.bottom
        self.y = float(self.hitbox.y)

    def resolve_peer_collisions(self, enemies):
        for other in enemies:
            if other is self:
                continue
            if not self.hitbox.colliderect(other.hitbox):
                continue
            overlap_x = min(self.hitbox.right, other.hitbox.right) - max(self.hitbox.left, other.hitbox.left)
            overlap_y = min(self.hitbox.bottom, other.hitbox.bottom) - max(self.hitbox.top, other.hitbox.top)
            if overlap_x < overlap_y:
                if self.hitbox.centerx < other.hitbox.centerx:
                    self.hitbox.right = other.hitbox.left
                else:
                    self.hitbox.left = other.hitbox.right
            else:
                if self.hitbox.centery < other.hitbox.centery:
                    self.hitbox.bottom = other.hitbox.top
                else:
                    self.hitbox.top = other.hitbox.bottom
            self.x = float(self.hitbox.x)
            self.y = float(self.hitbox.y)

class MeleeEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 3.5, 15)
        self.agro_radius = 700
        self.attack_range = 50
        self.attack_cooldown = 1000

        self.hitbox = pygame.Rect(0, 0, settings.TILE_SIZE - 25, settings.TILE_SIZE - 25)
        self.hitbox.x = x
        self.hitbox.y = y
        self.x = float(self.hitbox.x)
        self.y = float(self.hitbox.y)

        self.is_dead = False
        self.facing = "right"
        self.state = "idle"
        
        size = int(settings.TILE_SIZE * 3)

        def cut_strip(filename, frames_count, flip=False):
            try:
                strip = pygame.image.load(filename).convert_alpha()
            except FileNotFoundError:
                img = pygame.Surface((size, size))
                img.fill((200, 50, 50))
                return [img] * frames_count
                
            frame_w = strip.get_width() // frames_count
            strip_h = strip.get_height()
            frames = []
            for i in range(frames_count):
                rect = pygame.Rect(i * frame_w, 0, frame_w, strip_h)
                frame = strip.subsurface(rect)
                frame = pygame.transform.scale(frame, (size, size))
                if flip:
                    frame = pygame.transform.flip(frame, True, False)
                frames.append(frame)
            return frames

        self.anim_idle_right = cut_strip(os.path.join("assets", "red_slime_idle.png"), 4)
        self.anim_idle_left = cut_strip(os.path.join("assets", "red_slime_idle.png"), 4, flip=True)
        
        self.anim_walk_right = cut_strip(os.path.join("assets", "red_slime_walk.png"), 8)
        self.anim_walk_left = cut_strip(os.path.join("assets", "red_slime_walk.png"), 8, flip=True)
        
        self.anim_death_right = cut_strip(os.path.join("assets", "red_slime_death.png"), 10)
        self.anim_death_left = cut_strip(os.path.join("assets", "red_slime_death.png"), 10, flip=True)
        
        self.anim_list = self.anim_idle_right
        self.frame_index = 0
        self.anim_timer = pygame.time.get_ticks()
        self.anim_speed = 100
        self.image = self.anim_list[self.frame_index]
        self.rect = self.image.get_rect()

    def take_damage(self, amount):
        if self.is_dead:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True
            self.state = "dead"
            self.frame_index = 0
            return True
        return False

    def animate(self):
        prev_anim = self.anim_list
        
        if self.state == "dead":
            self.anim_list = self.anim_death_right if self.facing == "right" else self.anim_death_left
        elif self.state == "walk":
            self.anim_list = self.anim_walk_right if self.facing == "right" else self.anim_walk_left
        else:
            self.anim_list = self.anim_idle_right if self.facing == "right" else self.anim_idle_left
            
        if prev_anim != self.anim_list:
            self.frame_index = 0
            
        now = pygame.time.get_ticks()
        if now - self.anim_timer > self.anim_speed:
            self.anim_timer = now
            if self.state == "dead":
                if self.frame_index < len(self.anim_list) - 1:
                    self.frame_index += 1
                else:
                    self.kill()
            else:
                self.frame_index += 1
                if self.frame_index >= len(self.anim_list):
                    self.frame_index = 0
                    
        self.image = self.anim_list[self.frame_index]

    def update(self, player, walls, enemy_bullets):
        if self.is_dead:
            self.animate()
            return

        dx = player.hitbox.centerx - self.hitbox.centerx
        dy = player.hitbox.centery - self.hitbox.centery
        dist = (dx * dx + dy * dy) ** 0.5
        
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

        is_moving = False

        if dist < self.agro_radius:
            if dist > self.attack_range:
                self._move_towards(player.hitbox.centerx, player.hitbox.centery, walls)
                is_moving = True
                
        if dist < self.attack_range:
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.attack_cooldown:
                player.take_damage(self.damage)
                self.last_attack = now
                
        self.state = "walk" if is_moving else "idle"
        self.animate()
        
        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom + 85

class RangedEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 1.5, 10)
        self.agro_radius = 700
        self.preferred_dist = 200
        self.shoot_cooldown = 1500

        self.hitbox = pygame.Rect(0, 0, settings.TILE_SIZE - 25, settings.TILE_SIZE - 25)
        self.hitbox.x = x
        self.hitbox.y = y
        self.x = float(self.hitbox.x)
        self.y = float(self.hitbox.y)

        self.is_dead = False
        self.facing = "right"
        self.state = "idle"
        
        size = int(settings.TILE_SIZE * 3)

        def cut_strip(filename, frames_count, flip=False):
            try:
                strip = pygame.image.load(filename).convert_alpha()
            except FileNotFoundError:
                img = pygame.Surface((size, size))
                img.fill((150, 50, 200)) 
                return [img] * frames_count
                
            frame_w = strip.get_width() // frames_count
            strip_h = strip.get_height()
            frames = []
            for i in range(frames_count):
                rect = pygame.Rect(i * frame_w, 0, frame_w, strip_h)
                frame = strip.subsurface(rect)
                frame = pygame.transform.scale(frame, (size, size))
                if flip:
                    frame = pygame.transform.flip(frame, True, False)
                frames.append(frame)
            return frames

        self.anim_idle_right = cut_strip(os.path.join("assets", "slime_idle.png"), 4)
        self.anim_idle_left = cut_strip(os.path.join("assets", "slime_idle.png"), 4, flip=True)
        
        self.anim_walk_right = cut_strip(os.path.join("assets", "slime_walk.png"), 8)
        self.anim_walk_left = cut_strip(os.path.join("assets", "slime_walk.png"), 8, flip=True)
        
        self.anim_death_right = cut_strip(os.path.join("assets", "slime_death.png"), 10)
        self.anim_death_left = cut_strip(os.path.join("assets", "slime_death.png"), 10, flip=True)
        
        self.anim_list = self.anim_idle_right
        self.frame_index = 0
        self.anim_timer = pygame.time.get_ticks()
        self.anim_speed = 100
        self.image = self.anim_list[self.frame_index]
        self.rect = self.image.get_rect()

    def take_damage(self, amount):
        if self.is_dead:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True
            self.state = "dead"
            self.frame_index = 0
            return True
        return False

    def animate(self):
        prev_anim = self.anim_list
        
        if self.state == "dead":
            self.anim_list = self.anim_death_right if self.facing == "right" else self.anim_death_left
        elif self.state == "walk":
            self.anim_list = self.anim_walk_right if self.facing == "right" else self.anim_walk_left
        else:
            self.anim_list = self.anim_idle_right if self.facing == "right" else self.anim_idle_left
            
        if prev_anim != self.anim_list:
            self.frame_index = 0
            
        now = pygame.time.get_ticks()
        if now - self.anim_timer > self.anim_speed:
            self.anim_timer = now
            if self.state == "dead":
                if self.frame_index < len(self.anim_list) - 1:
                    self.frame_index += 1
                else:
                    self.kill()
            else:
                self.frame_index += 1
                if self.frame_index >= len(self.anim_list):
                    self.frame_index = 0
                    
        self.image = self.anim_list[self.frame_index]

    def update(self, player, walls, enemy_bullets):
        if self.is_dead:
            self.animate()
            return

        dx = player.hitbox.centerx - self.hitbox.centerx
        dy = player.hitbox.centery - self.hitbox.centery
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

        is_moving = False
        
        if dist < self.agro_radius:
            if dist > self.preferred_dist:
                self._move_towards(player.hitbox.centerx, player.hitbox.centery, walls)
                is_moving = True
            elif dist < self.preferred_dist - 40:
                self._move_towards(self.hitbox.centerx - dx, self.hitbox.centery - dy, walls)
                is_moving = True
                
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.shoot_cooldown:
                ndx, ndy = dx / dist, dy / dist
                bullet = EnemyBullet(self.hitbox.centerx, self.hitbox.centery, ndx, ndy, self.damage, "green")
                enemy_bullets.add(bullet)
                self.last_attack = now
                
        self.state = "walk" if is_moving else "idle"
        self.animate()
        
        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom + 85 

class TriangleRangedEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 35, 1.7, 8)
        self.agro_radius = 700
        self.preferred_dist = 200
        self.shoot_cooldown = 2200

        self.hitbox = pygame.Rect(0, 0, settings.TILE_SIZE - 25, settings.TILE_SIZE - 25)
        self.hitbox.x = x
        self.hitbox.y = y
        self.x = float(self.hitbox.x)
        self.y = float(self.hitbox.y)

        self.is_dead = False
        self.facing = "right"
        self.state = "idle"
        
        size = int(settings.TILE_SIZE * 3)

        def cut_strip(filename, frames_count, flip=False):
            try:
                strip = pygame.image.load(filename).convert_alpha()
            except FileNotFoundError:
                img = pygame.Surface((size, size))
                img.fill((170, 80, 170))
                return [img] * frames_count
                
            frame_w = strip.get_width() // frames_count
            strip_h = strip.get_height()
            frames = []
            for i in range(frames_count):
                rect = pygame.Rect(i * frame_w, 0, frame_w, strip_h)
                frame = strip.subsurface(rect)
                frame = pygame.transform.scale(frame, (size, size))
                if flip:
                    frame = pygame.transform.flip(frame, True, False)
                frames.append(frame)
            return frames

        self.anim_idle_right = cut_strip(os.path.join("assets", "purple_slime_idle.png"), 4)
        self.anim_idle_left = cut_strip(os.path.join("assets", "purple_slime_idle.png"), 4, flip=True)
        
        self.anim_walk_right = cut_strip(os.path.join("assets", "purple_slime_walk.png"), 8)
        self.anim_walk_left = cut_strip(os.path.join("assets", "purple_slime_walk.png"), 8, flip=True)
        
        self.anim_death_right = cut_strip(os.path.join("assets", "purple_slime_death.png"), 10)
        self.anim_death_left = cut_strip(os.path.join("assets", "purple_slime_death.png"), 10, flip=True)
        
        self.anim_list = self.anim_idle_right
        self.frame_index = 0
        self.anim_timer = pygame.time.get_ticks()
        self.anim_speed = 100
        self.image = self.anim_list[self.frame_index]
        self.rect = self.image.get_rect()

    def take_damage(self, amount):
        if self.is_dead:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True
            self.state = "dead"
            self.frame_index = 0
            return True
        return False

    def animate(self):
        prev_anim = self.anim_list
        
        if self.state == "dead":
            self.anim_list = self.anim_death_right if self.facing == "right" else self.anim_death_left
        elif self.state == "walk":
            self.anim_list = self.anim_walk_right if self.facing == "right" else self.anim_walk_left
        else:
            self.anim_list = self.anim_idle_right if self.facing == "right" else self.anim_idle_left
            
        if prev_anim != self.anim_list:
            self.frame_index = 0
            
        now = pygame.time.get_ticks()
        if now - self.anim_timer > self.anim_speed:
            self.anim_timer = now
            if self.state == "dead":
                if self.frame_index < len(self.anim_list) - 1:
                    self.frame_index += 1
                else:
                    self.kill()
            else:
                self.frame_index += 1
                if self.frame_index >= len(self.anim_list):
                    self.frame_index = 0
                    
        self.image = self.anim_list[self.frame_index]

    def _rotate_vector(self, dx, dy, angle_degrees):
        angle = math.radians(angle_degrees)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return dx * cos_a - dy * sin_a, dx * sin_a + dy * cos_a

    def update(self, player, walls, enemy_bullets):
        if self.is_dead:
            self.animate()
            return

        dx = player.hitbox.centerx - self.hitbox.centerx
        dy = player.hitbox.centery - self.hitbox.centery
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

        is_moving = False
        
        if dist < self.agro_radius:
            if dist > self.preferred_dist:
                self._move_towards(player.hitbox.centerx, player.hitbox.centery, walls)
                is_moving = True
            elif dist < self.preferred_dist - 40:
                self._move_towards(self.hitbox.centerx - dx, self.hitbox.centery - dy, walls)
                is_moving = True
                
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.shoot_cooldown:
                ndx, ndy = dx / dist, dy / dist
                center = (ndx, ndy)
                left = self._rotate_vector(ndx, ndy, 30)
                right = self._rotate_vector(ndx, ndy, -30)
                for vx, vy in (center, left, right):
                    bullet = EnemyBullet(self.hitbox.centerx, self.hitbox.centery, vx, vy, self.damage, "purple")
                    enemy_bullets.add(bullet)
                self.last_attack = now
                
        self.state = "walk" if is_moving else "idle"
        self.animate()
        
        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom + 85


class BurstRangedEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 45, 1.3, 8)
        self.agro_radius = 700
        self.preferred_dist = 190
        self.burst_cooldown = 2600
        self.burst_interval_ms = 95
        self._burst_remaining = 0
        self._next_burst_shot = 0
        self.last_attack = pygame.time.get_ticks()

        self.hitbox = pygame.Rect(0, 0, settings.TILE_SIZE - 25, settings.TILE_SIZE - 25)
        self.hitbox.x = x
        self.hitbox.y = y
        self.x = float(self.hitbox.x)
        self.y = float(self.hitbox.y)

        self.is_dead = False
        self.facing = "right"
        self.state = "idle"
        
        size = int(settings.TILE_SIZE * 3)

        def cut_strip(filename, frames_count, flip=False):
            try:
                strip = pygame.image.load(filename).convert_alpha()
            except FileNotFoundError:
                img = pygame.Surface((size, size))
                img.fill((80, 40, 160)) 
                return [img] * frames_count
                
            frame_w = strip.get_width() // frames_count
            strip_h = strip.get_height()
            frames = []
            for i in range(frames_count):
                rect = pygame.Rect(i * frame_w, 0, frame_w, strip_h)
                frame = strip.subsurface(rect)
                frame = pygame.transform.scale(frame, (size, size))
                if flip:
                    frame = pygame.transform.flip(frame, True, False)
                frames.append(frame)
            return frames

        self.anim_idle_right = cut_strip(os.path.join("assets", "purple_slime_idle.png"), 4)
        self.anim_idle_left = cut_strip(os.path.join("assets", "purple_slime_idle.png"), 4, flip=True)
        
        self.anim_walk_right = cut_strip(os.path.join("assets", "purple_slime_walk.png"), 8)
        self.anim_walk_left = cut_strip(os.path.join("assets", "purple_slime_walk.png"), 8, flip=True)
        
        self.anim_death_right = cut_strip(os.path.join("assets", "purple_slime_death.png"), 10)
        self.anim_death_left = cut_strip(os.path.join("assets", "purple_slime_death.png"), 10, flip=True)
        
        self.anim_list = self.anim_idle_right
        self.frame_index = 0
        self.anim_timer = pygame.time.get_ticks()
        self.anim_speed = 100
        self.image = self.anim_list[self.frame_index]
        self.rect = self.image.get_rect()

    def take_damage(self, amount):
        if self.is_dead:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True
            self.state = "dead"
            self.frame_index = 0
            return True
        return False

    def animate(self):
        prev_anim = self.anim_list
        
        if self.state == "dead":
            self.anim_list = self.anim_death_right if self.facing == "right" else self.anim_death_left
        elif self.state == "walk":
            self.anim_list = self.anim_walk_right if self.facing == "right" else self.anim_walk_left
        else:
            self.anim_list = self.anim_idle_right if self.facing == "right" else self.anim_idle_left
            
        if prev_anim != self.anim_list:
            self.frame_index = 0
            
        now = pygame.time.get_ticks()
        if now - self.anim_timer > self.anim_speed:
            self.anim_timer = now
            if self.state == "dead":
                if self.frame_index < len(self.anim_list) - 1:
                    self.frame_index += 1
                else:
                    self.kill()
            else:
                self.frame_index += 1
                if self.frame_index >= len(self.anim_list):
                    self.frame_index = 0
                    
        self.image = self.anim_list[self.frame_index]

    def update(self, player, walls, enemy_bullets):
        if self.is_dead:
            self.animate()
            return

        dx = player.hitbox.centerx - self.hitbox.centerx
        dy = player.hitbox.centery - self.hitbox.centery
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

        is_moving = False

        if dist < self.agro_radius:
            if dist > self.preferred_dist:
                self._move_towards(player.hitbox.centerx, player.hitbox.centery, walls)
                is_moving = True
            elif dist < self.preferred_dist - 40:
                self._move_towards(self.hitbox.centerx - dx, self.hitbox.centery - dy, walls)
                is_moving = True

        now = pygame.time.get_ticks()
        ndx, ndy = dx / dist, dy / dist

        if self._burst_remaining > 0:
            if now >= self._next_burst_shot:
                bullet = EnemyBullet(self.hitbox.centerx, self.hitbox.centery, ndx, ndy, self.damage, "purple")
                enemy_bullets.add(bullet)
                self._burst_remaining -= 1
                if self._burst_remaining > 0:
                    self._next_burst_shot = now + self.burst_interval_ms
                else:
                    self.last_attack = now
        elif dist < self.agro_radius and now - self.last_attack > self.burst_cooldown:
            bullet = EnemyBullet(self.hitbox.centerx, self.hitbox.centery, ndx, ndy, self.damage, "purple")
            enemy_bullets.add(bullet)
            self._burst_remaining = 2
            self._next_burst_shot = now + self.burst_interval_ms

        self.state = "walk" if is_moving else "idle"
        self.animate()
        
        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom + 85