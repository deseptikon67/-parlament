import pygame


class Merchant:
    def __init__(self, x, y):
        self.bag_image = pygame.image.load("assets/bag.png").convert_alpha()
        self.bag_image = pygame.transform.scale(self.bag_image, (400, 400))

        self.image = pygame.image.load("assets/lekar.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 90))

        # 🧾 окно магазина (КАРТИНКА)
        self.shop_image = pygame.image.load("assets/shop.png").convert_alpha()

        self.rect = self.image.get_rect(center=(x, y))

        # зона активации
        self.zone = pygame.Rect(0, 0, 160, 120)
        self.zone.center = self.rect.center

        self.active = False

        # кнопка (ИСПОЛЬЗУЕТСЯ ДЛЯ КЛИКА)
        self.btn_heal = pygame.Rect(0, 0, 0, 0)

        # ❌ сообщение об ошибке
        self.error_text = ""
        self.error_time = 0

    def update(self, player):
        self.zone.center = self.rect.center
        self.active = self.zone.colliderect(player.rect)

    def draw(self, surface, camera):

        # --- мешок ---
        bag_rect = self.bag_image.get_rect()
        bag_rect.center = (self.rect.centerx + 70, self.rect.centery - 30)
        surface.blit(self.bag_image, camera.apply(bag_rect))

        # --- торговец ---
        surface.blit(self.image, camera.apply(self.rect))

        if not self.active:
            return

        w, h = surface.get_size()

        # --- окно магазина ---
        panel = self.shop_image.get_rect()
        panel.center = (w // 2, h // 2)

        surface.blit(self.shop_image, panel.topleft)

        # ============================
        # 🔥 КНОПКА ДЛЯ НАСТРОЙКИ (DEBUG)
        # ============================

        self.btn_heal.width = int(panel.width * 0.5)
        self.btn_heal.height = 160
        self.btn_heal.centerx = panel.centerx
        self.btn_heal.top = panel.top + int(panel.height * 0.5)

        # ----------------------------
        # 🟢 ВИЗУАЛ КНОПКИ (ЗАКОММЕНЧЕНО)
        # ----------------------------

        """
        pygame.draw.rect(
            surface,
            (0, 200, 0),
            self.btn_heal,
            border_radius=10
        )

        font = pygame.font.SysFont("Arial", 24, bold=True)
        text = font.render("Вылечиться (10)", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.btn_heal.center)
        surface.blit(text, text_rect)
        """

        # ❌ сообщение об ошибке
        if self.error_text:
            if pygame.time.get_ticks() - self.error_time < 2000:
                font = pygame.font.SysFont("Arial", 28, bold=True)

                text = font.render(self.error_text, True, (255, 50, 50))
                text_rect = text.get_rect(center=(w // 2, h // 2 - 140))

                surface.blit(text, text_rect)
            else:
                self.error_text = ""

    def handle_click(self, player, pos):
        if not self.active:
            return None

        if self.btn_heal.collidepoint(pos):
            if player.gold >= 10:
                player.gold -= 10
                player.hp = player.max_hp
                return "heal"
            else:
                # ❌ недостаточно золота
                self.error_text = "Недостаточно золота"
                self.error_time = pygame.time.get_ticks()

        return None