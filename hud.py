import pygame
import settings


class HUD:
    def draw(self, surface, player, current_floor):
        w, h = surface.get_size()

        margin = max(15, int(w * 0.015))
        font_size = max(18, int(h * 0.03))
        font = pygame.font.SysFont("Arial", font_size, bold=True)

        bar_w = max(180, int(w * 0.2))
        bar_h = max(14, int(h * 0.02))

        ratio = player.hp / player.max_hp if player.max_hp else 0
        fill_w = int(bar_w * ratio)

        if ratio > 0.6:
            color = (0, 200, 0)
        elif ratio > 0.3:
            color = (220, 200, 0)
        else:
            color = (200, 0, 0)

        pygame.draw.rect(surface, (80, 80, 80),
                         (margin, margin, bar_w, bar_h))
        pygame.draw.rect(surface, color,
                         (margin, margin, fill_w, bar_h))

        y = margin + bar_h + 6

        surface.blit(font.render(
            f"HP: {player.hp}/{player.max_hp}",
            True,
            (255, 255, 255)
        ), (margin, y))

        y += font_size + 4

        surface.blit(font.render(
            f"Этаж: {current_floor}",
            True,
            (255, 215, 0)
        ), (margin, y))

        y += font_size + 4

        surface.blit(font.render(
            f"Золото: {player.gold}",
            True,
            (255, 215, 0)
        ), (margin, y))

        y += font_size + 4

        surface.blit(font.render(
            f"Уровень: {player.level} | {player.exp}/{player.exp_to_next_level}",
            True,
            (0, 255, 0)
        ), (margin, y))


class PauseMenu:
    def __init__(self):
        self.active = False
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_btn = pygame.font.SysFont(None, 40)

        self.btn_resume = pygame.Rect(0, 0, 240, 50)
        self.btn_quit = pygame.Rect(0, 0, 240, 50)

    def draw(self, surface):
        w, h = surface.get_size()

        self.btn_resume.center = (w // 2, h // 2 - 30)
        self.btn_quit.center = (w // 2, h // 2 + 40)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("ПАУЗА", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 120)))

        pygame.draw.rect(surface, (50, 50, 50), self.btn_resume, border_radius=8)
        pygame.draw.rect(surface, (50, 50, 50), self.btn_quit, border_radius=8)

        surface.blit(self.font_btn.render("Продолжить", True, (255, 255, 255)),
                     self.font_btn.render("Продолжить", True, (255, 255, 255)).get_rect(center=self.btn_resume.center))

        surface.blit(self.font_btn.render("Выйти", True, (255, 255, 255)),
                     self.font_btn.render("Выйти", True, (255, 255, 255)).get_rect(center=self.btn_quit.center))

    def handle_click(self, mouse_pos):
        if self.btn_resume.collidepoint(mouse_pos):
            self.active = False
            return "resume"
        if self.btn_quit.collidepoint(mouse_pos):
            return "quit"
        return None


class DeathMenu:
    def __init__(self):
        self.active = False
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_btn = pygame.font.SysFont(None, 40)

        self.btn_restart = pygame.Rect(0, 0, 240, 50)
        self.btn_quit = pygame.Rect(0, 0, 240, 50)

    def draw(self, surface):
        w, h = surface.get_size()

        self.btn_restart.center = (w // 2, h // 2 - 30)
        self.btn_quit.center = (w // 2, h // 2 + 40)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("ВЫ ПОГИБЛИ", True, (200, 0, 0))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 120)))

        pygame.draw.rect(surface, (50, 50, 50), self.btn_restart, border_radius=8)
        pygame.draw.rect(surface, (50, 50, 50), self.btn_quit, border_radius=8)

        surface.blit(self.font_btn.render("Начать заново", True, (255, 255, 255)),
                     self.font_btn.render("Начать заново", True, (255, 255, 255)).get_rect(center=self.btn_restart.center))

        surface.blit(self.font_btn.render("Выйти", True, (255, 255, 255)),
                     self.font_btn.render("Выйти", True, (255, 255, 255)).get_rect(center=self.btn_quit.center))

    def handle_click(self, mouse_pos):
        if self.btn_restart.collidepoint(mouse_pos):
            return "restart"
        if self.btn_quit.collidepoint(mouse_pos):
            return "quit"
        return None



