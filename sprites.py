import pygame
import settings

class Player(pygame.sprite.Sprite):
    def __init__(self,x, y):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE - 10, settings.TILE_SIZE - 10))
        self.image.fill(settings.GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x * settings.TILE_SIZE
        self.rect.y = y * settings.TILE_SIZE
        self.speed = settings.PLAYER_SPEED

    def update(self, walls):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.right = wall.rect.left
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.left = wall.rect.right

        # --- ВЕРТИКАЛЬ (Y) ---
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Проверяем столкновения по Y сразу после движения
        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:  # Идем вниз
                self.rect.bottom = wall.rect.top
            if keys[pygame.K_UP] or keys[pygame.K_w]:  # Идем вверх
                self.rect.top = wall.rect.bottom

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        self.image.fill(settings.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y