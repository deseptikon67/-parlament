import pygame
import settings

# Физические позиции клавиш (US QWERTY): раскладка и Caps Lock не влияют.
if hasattr(pygame, "KSCAN_A"):
    _SCAN_A = pygame.KSCAN_A
    _SCAN_D = pygame.KSCAN_D
    _SCAN_S = pygame.KSCAN_S
    _SCAN_W = pygame.KSCAN_W
else:
    _SCAN_A, _SCAN_D, _SCAN_S, _SCAN_W = 4, 7, 22, 26


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE - 10, settings.TILE_SIZE - 10))
        self.image.fill(settings.GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x * settings.TILE_SIZE
        self.rect.y = y * settings.TILE_SIZE
        self.speed = settings.PLAYER_SPEED
        self.facing = "right"
        self.hp = 100
        self.max_hp = 100
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1000
        self.shoot_cooldown = 300
        self.last_shot = 0
        self.bullet_damage = 20

    def take_damage(self, amount):
        if self.invincible:
            return False
        self.hp = max(0, self.hp - amount)
        self.invincible = True
        self.invincible_timer = pygame.time.get_ticks()
        return self.hp == 0

    def _shoot(self, keys, bullet_group):
        from enemies import PlayerBullet

        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            return
        if keys[pygame.K_RIGHT]:
            dx, dy = 1, 0
        elif keys[pygame.K_LEFT]:
            dx, dy = -1, 0
        elif keys[pygame.K_DOWN]:
            dx, dy = 0, 1
        elif keys[pygame.K_UP]:
            dx, dy = 0, -1
        else:
            return
        bullet = PlayerBullet(self.rect.centerx, self.rect.centery, dx, dy, self.bullet_damage)
        bullet_group.add(bullet)
        self.last_shot = now

    def update(self, walls, bullet_group):
        keys = pygame.key.get_pressed()
        get_sc = getattr(pygame.key, "get_scancode_pressed", None)
        if get_sc is not None:
            sc = get_sc()
            move_left = sc[_SCAN_A]
            move_right = sc[_SCAN_D]
            move_up = sc[_SCAN_W]
            move_down = sc[_SCAN_S]
        else:
            move_left = keys[pygame.K_a]
            move_right = keys[pygame.K_d]
            move_up = keys[pygame.K_w]
            move_down = keys[pygame.K_s]

        # --- ДВИЖЕНИЕ (физические WASD) ---
        if move_left:
            self.rect.x -= self.speed
            self.facing = "left"
        if move_right:
            self.rect.x += self.speed
            self.facing = "right"

        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if move_right:
                self.rect.right = wall.rect.left
            if move_left:
                self.rect.left = wall.rect.right

        if move_up:
            self.rect.y -= self.speed
            self.facing = "up"
        if move_down:
            self.rect.y += self.speed
            self.facing = "down"

        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if move_down:
                self.rect.bottom = wall.rect.top
            if move_up:
                self.rect.top = wall.rect.bottom

        # --- СТРЕЛЬБА (только стрелки) ---
        self._shoot(keys, bullet_group)

        # --- IFRAMES ---
        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > self.invincible_duration:
                self.invincible = False


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        self.image.fill(settings.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
