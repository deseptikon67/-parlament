import pygame
import settings
import sprites
import map_generator
# Инициализация
pygame.init()
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Название твоей игры")

# Группы спрайтов
all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()

game_map, spawn_x, spawn_y = map_generator.create_map(16, 12)
# Создаем игрока через модуль sprites 👾
player = sprites.Player(spawn_x, spawn_y)
all_sprites.add(player)

# Строим карту

for r in range(len(game_map)):
    for c in range(len(game_map[r])):
        if game_map[r][c] == 1:
            wall = sprites.Wall(c * settings.TILE_SIZE, r * settings.TILE_SIZE)
            all_sprites.add(wall)
            walls_group.add(wall)

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(settings.FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновление
    player.update(walls_group)

    # Отрисовка
    screen.fill(settings.BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()