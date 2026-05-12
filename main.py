import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
TILE_SIZE = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("фващтиващ")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 200, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5

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
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

 # --- ФУНКЦИИ ---
def create_map(cols, rows):
    # Создаем пол (везде 0)
    game_map = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            # Если это первая или последняя строка
            if r == 0 or r == rows - 1:
                game_map[r][c] = 1
            # Если это первый или последний столбец
            if c == 0 or c == cols - 1:
                game_map[r][c] = 1

    return game_map


all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
clock = pygame.time.Clock()


walls_group = pygame.sprite.Group() # Группа специально для стен

# Получаем план карты
game_map = create_map(16, 12)

# "Строим" стены
for r in range(len(game_map)):
    for c in range(len(game_map[r])):
        if game_map[r][c] == 1:
            # Создаем стену и добавляем в группы
            wall = Wall(c * TILE_SIZE, r * TILE_SIZE)
            all_sprites.add(wall)
            walls_group.add(wall)

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Обновляем логику
    player.update(walls_group)

# 3. Отрисовка
    screen.fill(BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()