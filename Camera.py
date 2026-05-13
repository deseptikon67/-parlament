import pygame
class Camera:
    def __init__(self, width, height):
        # width и height — это размеры всей твоей карты в пикселях
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, target_rect):
        # Сдвигает прямоугольник объекта относительно положения камеры
        return target_rect.move(self.camera.topleft)

    def update(self, target, screen_width, screen_height):
        # Вычисляем сдвиг: центр экрана минус позиция игрока
        x = -target.rect.centerx + int(screen_width / 2)
        y = -target.rect.centery + int(screen_height / 2)

        self.camera = pygame.Rect(x, y, self.width, self.height)