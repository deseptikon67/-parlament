import pygame
import settings
import sprites
import map_generator
from settings import camera, WIDTH, HEIGHT
# Инициализация
pygame.init()
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("оттл")


# Группы спрайтов
all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()


game_map, spawn_x, spawn_y = map_generator.create_map(settings.MAP_COLS, settings.MAP_ROWS)
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
    # 1. ЛОГИКА
    clock.tick(settings.FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновляем камеру и игрока
    camera.update(player, WIDTH, HEIGHT)
    player.update(walls_group)

    # 2. ОТРИСОВКА
    screen.fill(settings.BLACK)  # Или settings.WHITE, смотря какой фон хочешь

    # Рисуем стены через камеру
    for wall in walls_group:
        screen.blit(wall.image, camera.apply(wall.rect))

    # Рисуем игрока через камеру
    screen.blit(player.image, camera.apply(player.rect))

    # Выводим всё на экран
    pygame.display.flip()

pygame.quit()