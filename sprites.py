import pygame
import settings
from modifiers import BuffManager

try:
    _SCAN_A = pygame.KSCAN_A
    _SCAN_D = pygame.KSCAN_D
    _SCAN_S = pygame.KSCAN_S
    _SCAN_W = pygame.KSCAN_W
except AttributeError:
    _SCAN_A, _SCAN_D, _SCAN_S, _SCAN_W = 4, 7, 22, 26

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.visual_size = int(settings.TILE_SIZE * 2.5)
        
        def cut_strip(filename):
            frames_count = 8 
            try:
                strip = pygame.image.load(filename).convert_alpha()
            except FileNotFoundError:
                img = pygame.Surface((self.visual_size, self.visual_size))
                img.fill(settings.GREEN)
                return [img] * frames_count
                
            frame_width = strip.get_width() // frames_count
            strip_height = strip.get_height()
            frames = []
            for i in range(frames_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, strip_height)
                frame = strip.subsurface(rect)
                frame = pygame.transform.scale(frame, (self.visual_size, self.visual_size))
                frames.append(frame)
            return frames

        # --- ЗАГРУЖАЕМ АНИМАЦИИ ПОКОЯ (IDLE) ---
        self.idle_down = cut_strip("assets/idle_down.png")
        self.idle_up = cut_strip("assets/idle_up.png")
        self.idle_left_down = cut_strip("assets/idle_left_down.png")
        self.idle_left_up = cut_strip("assets/idle_left_up.png")
        self.idle_right_down = cut_strip("assets/idle_right_down.png")
        self.idle_right_up = cut_strip("assets/idle_right_up.png")
        
        # --- ЗАГРУЖАЕМ АНИМАЦИИ ХОДЬБЫ (WALK) ---
        self.walk_down = cut_strip("assets/walk_down.png")
        self.walk_up = cut_strip("assets/walk_up.png")
        self.walk_left_down = cut_strip("assets/walk_left_down.png")
        self.walk_left_up = cut_strip("assets/walk_left_up.png")
        self.walk_right_down = cut_strip("assets/walk_right_down.png")
        self.walk_right_up = cut_strip("assets/walk_right_up.png")

        # --- ЗАГРУЖАЕМ АНИМАЦИИ СМЕРТИ (DEATH) ---
        # Проверь названия файлов в папке assets!
        self.death_down = cut_strip("assets/death_down.png")
        self.death_up = cut_strip("assets/death_up.png")
        self.death_left_down = cut_strip("assets/death_left_down.png")
        self.death_left_up = cut_strip("assets/death_left_up.png")
        self.death_right_down = cut_strip("assets/death_right_down.png")
        self.death_right_up = cut_strip("assets/death_right_up.png")
        
        # --- НАСТРОЙКИ АНИМАЦИИ ---
        self.anim_list = self.idle_down
        self.frame_index = 0
        self.image = self.anim_list[self.frame_index]
        self.anim_timer = pygame.time.get_ticks()
        self.anim_speed = 100 
        
        # --- ФИЗИКА И СОСТОЯНИЕ ---
        self.rect = self.image.get_rect()
        self.hitbox = pygame.Rect(0, 0, settings.TILE_SIZE - 10, settings.TILE_SIZE - 10)
        self.hitbox.x = x * settings.TILE_SIZE
        self.hitbox.y = y * settings.TILE_SIZE
        
        self.speed = settings.PLAYER_SPEED
        self.facing = "down"
        self.is_moving = False  
        self.is_dead = False
        self.death_time = 0
        
        self.hp = 100
        self.max_hp = 100
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1000
        self.last_shot = 0
        self.bullet_damage = 20
        self.base_speed = settings.PLAYER_SPEED
        self.base_shoot_cooldown = 300
        self.buff_manager = BuffManager()

    # --- МЕТОД АНИМАЦИИ ---
    def animate(self):
        prev_anim = self.anim_list

        # 1. ВЫБИРАЕМ СПИСОК АНИМАЦИИ В ЗАВИСИМОСТИ ОТ СОСТОЯНИЯ
        if self.is_dead:
            # Если мертв, ставим анимацию смерти
            if self.facing == "down": self.anim_list = self.death_down
            elif self.facing == "up": self.anim_list = self.death_up
            elif self.facing == "left_down": self.anim_list = self.death_left_down
            elif self.facing == "left_up": self.anim_list = self.death_left_up
            elif self.facing == "right_down": self.anim_list = self.death_right_down
            elif self.facing == "right_up": self.anim_list = self.death_right_up
        else:
            # Если жив, выбираем между ходьбой и простоем
            if self.facing == "down": self.anim_list = self.walk_down if self.is_moving else self.idle_down
            elif self.facing == "up": self.anim_list = self.walk_up if self.is_moving else self.idle_up
            elif self.facing == "left_down": self.anim_list = self.walk_left_down if self.is_moving else self.idle_left_down
            elif self.facing == "left_up": self.anim_list = self.walk_left_up if self.is_moving else self.idle_left_up
            elif self.facing == "right_down": self.anim_list = self.walk_right_down if self.is_moving else self.idle_right_down
            elif self.facing == "right_up": self.anim_list = self.walk_right_up if self.is_moving else self.idle_right_up

        if prev_anim != self.anim_list:
            self.frame_index = 0

        # 2. ПЕРЕЛИСТЫВАЕМ КАДРЫ
        now = pygame.time.get_ticks()
        if now - self.anim_timer > self.anim_speed:
            self.anim_timer = now
            
            if self.is_dead:
                # ЕСЛИ МЕРТВ: останавливаемся на последнем кадре
                if self.frame_index < len(self.anim_list) - 1:
                    self.frame_index += 1
                
            else:
                # ЕСЛИ ЖИВ: крутим анимацию по кругу
                self.frame_index += 1
                if self.frame_index >= len(self.anim_list):
                    self.frame_index = 0
                
        self.image = self.anim_list[self.frame_index]

    def take_damage(self, amount):
        # Если уже мертв или бессмертен, урон не проходит
        if self.invincible or self.is_dead:
            return False

        amount = int(amount * self.buff_manager.get_multiplier("damage_taken"))
        self.hp = max(0, self.hp - amount)
        
        # Если ХП упало до 0 — персонаж умирает
        if self.hp == 0:
            self.is_dead = True
            self.frame_index = 0
            self.death_time = pygame.time.get_ticks()
        else:
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            
        return self.hp == 0

    def _shoot(self, keys, bullet_group):
        from enemies import PlayerBullet

        now = pygame.time.get_ticks()
        cooldown = int(self.base_shoot_cooldown * self.buff_manager.get_multiplier("shoot_cooldown"))
        if now - self.last_shot < cooldown:
            return
        if keys[pygame.K_RIGHT]: dx, dy = 1, 0
        elif keys[pygame.K_LEFT]: dx, dy = -1, 0
        elif keys[pygame.K_DOWN]: dx, dy = 0, 1
        elif keys[pygame.K_UP]: dx, dy = 0, -1
        else: return
        
        bullet = PlayerBullet(self.rect.centerx, self.rect.centery, dx, dy, self.bullet_damage)
        bullet_group.add(bullet)
        self.last_shot = now

    def update(self, walls, bullet_group):
        # ==========================================
        # ЕСЛИ МЕРТВ - ТОЛЬКО ЛЕЖИМ (Выходим из update)
        # ==========================================
        if self.is_dead:
            self.animate()
            return  # Слово return обрывает функцию. Двигаться и стрелять он не сможет.

        # Дальше идет обычный код для живого игрока
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

        self.is_moving = move_left or move_right or move_up or move_down

        self.speed = int(self.base_speed * self.buff_manager.get_multiplier("move_speed"))

        if move_left and move_up: self.facing = "left_up"
        elif move_left and move_down: self.facing = "left_down"
        elif move_right and move_up: self.facing = "right_up"
        elif move_right and move_down: self.facing = "right_down"
        elif move_left: self.facing = "left_down"   
        elif move_right: self.facing = "right_down" 
        elif move_up: self.facing = "up"
        elif move_down: self.facing = "down"

        if move_left: self.hitbox.x -= self.speed
        if move_right: self.hitbox.x += self.speed

        for wall in walls:
            if self.hitbox.colliderect(wall.rect):
                if move_right: self.hitbox.right = wall.rect.left
                if move_left: self.hitbox.left = wall.rect.right

        if move_up: self.hitbox.y -= self.speed
        if move_down: self.hitbox.y += self.speed

        for wall in walls:
            if self.hitbox.colliderect(wall.rect):
                if move_down: self.hitbox.bottom = wall.rect.top
                if move_up: self.hitbox.top = wall.rect.bottom

        self.rect.midbottom = self.hitbox.midbottom

        self._shoot(keys, bullet_group)

        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > self.invincible_duration:
                self.invincible = False

        self.animate()

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        self.image.fill(settings.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y