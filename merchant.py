import pygame


class Merchant:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 60))
        self.image.fill((200, 150, 50))

        self.rect = self.image.get_rect(center=(x, y))

        # зона активации
        self.zone = pygame.Rect(0, 0, 160, 120)
        self.zone.center = self.rect.center

        self.active = False

        self.font = pygame.font.SysFont("Arial", 24, bold=True)

        self.btn_heal = pygame.Rect(0, 0, 200, 50)
        self.btn_card = pygame.Rect(0, 0, 200, 50)

    def update(self, player):
        self.active = self.zone.colliderect(player.rect)

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))

        if not self.active:
            return

        w, h = surface.get_size()

        # окно магазина по центру
        panel = pygame.Rect(w//2 - 150, h//2 - 120, 300, 200)

        pygame.draw.rect(surface, (30, 30, 30), panel)
        pygame.draw.rect(surface, (200, 150, 50), panel, 2)

        title = self.font.render("ТОРГОВЕЦ", True, (255, 255, 255))
        surface.blit(title, (panel.x + 80, panel.y + 10))

        self.btn_heal.topleft = (panel.x + 50, panel.y + 60)
        self.btn_card.topleft = (panel.x + 50, panel.y + 120)

        pygame.draw.rect(surface, (0, 200, 0), self.btn_heal)
        pygame.draw.rect(surface, (200, 200, 0), self.btn_card)

        surface.blit(self.font.render("Вылечиться (10)", True, (0,0,0)),
                     (self.btn_heal.x + 10, self.btn_heal.y + 10))

        surface.blit(self.font.render("Карточка (50)", True, (0,0,0)),
                     (self.btn_card.x + 10, self.btn_card.y + 10))

    def handle_click(self, player, pos):
        if not self.active:
            return None

        if self.btn_heal.collidepoint(pos):
            if player.gold >= 10:
                player.gold -= 10
                player.hp = player.max_hp
            return "heal"

        if self.btn_card.collidepoint(pos):
            if player.gold >= 50:
                player.gold -= 50
                return "card"

        return None