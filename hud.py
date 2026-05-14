import pygame

import settings


class HUD:
    def draw_player_hp(self, surface, player):
        bar_x, bar_y = 20, 20
        bar_w, bar_h = 200, 16
        ratio = player.hp / player.max_hp if player.max_hp else 0
        fill_w = int(bar_w * ratio)
        color = (0, 200, 0) if ratio > 0.6 else (220, 200, 0) if ratio > 0.3 else (200, 0, 0)
        pygame.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surface, color, (bar_x, bar_y, fill_w, bar_h))
        font = pygame.font.SysFont(None, 22)
        text = font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
        surface.blit(text, (bar_x, bar_y + bar_h + 4))


class PauseMenu:
    def __init__(self):
        self.active = False
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_btn = pygame.font.SysFont(None, 40)
        self.btn_resume = pygame.Rect(settings.WIDTH // 2 - 120, settings.HEIGHT // 2 - 30, 240, 50)
        self.btn_quit = pygame.Rect(settings.WIDTH // 2 - 120, settings.HEIGHT // 2 + 40, 240, 50)

    def draw(self, surface):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        title = self.font_title.render("ПАУЗА", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 100)))
        pygame.draw.rect(surface, (50, 50, 50), self.btn_resume, border_radius=8)
        pygame.draw.rect(surface, (50, 50, 50), self.btn_quit, border_radius=8)
        resume_surf = self.font_btn.render("Продолжить", True, (255, 255, 255))
        surface.blit(resume_surf, resume_surf.get_rect(center=self.btn_resume.center))
        quit_surf = self.font_btn.render("Выйти", True, (255, 255, 255))
        surface.blit(quit_surf, quit_surf.get_rect(center=self.btn_quit.center))

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
        self.btn_restart = pygame.Rect(settings.WIDTH // 2 - 120, settings.HEIGHT // 2 - 30, 240, 50)
        self.btn_quit = pygame.Rect(settings.WIDTH // 2 - 120, settings.HEIGHT // 2 + 40, 240, 50)

    def draw(self, surface):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        title = self.font_title.render("ВЫ ПОГИБЛИ", True, (200, 0, 0))
        surface.blit(title, title.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 100)))
        pygame.draw.rect(surface, (50, 50, 50), self.btn_restart, border_radius=8)
        pygame.draw.rect(surface, (50, 50, 50), self.btn_quit, border_radius=8)
        restart_surf = self.font_btn.render("Начать заново", True, (255, 255, 255))
        surface.blit(restart_surf, restart_surf.get_rect(center=self.btn_restart.center))
        quit_surf = self.font_btn.render("Выйти", True, (255, 255, 255))
        surface.blit(quit_surf, quit_surf.get_rect(center=self.btn_quit.center))

    def handle_click(self, mouse_pos):
        if self.btn_restart.collidepoint(mouse_pos):
            return "restart"
        if self.btn_quit.collidepoint(mouse_pos):
            return "quit"
        return None
