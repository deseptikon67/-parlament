from Camera import Camera

WIDTH = 800
HEIGHT = 600

FPS = 60
TILE_SIZE = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)

# Настройки игрока
PLAYER_SPEED = 5

MAP_COLS = 80
MAP_ROWS = 60
MAX_FLOORS = 3  # Количество этажей до финального экрана
camera = Camera(MAP_COLS * TILE_SIZE, MAP_ROWS * TILE_SIZE)