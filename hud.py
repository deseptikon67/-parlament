import pygame
import settings


class HUD:
    def draw(
        self,
        surface,
        player,
        current_floor,
        score_display=None,
        score_manager=None,
        run_timer=None
    ):
        w, h = surface.get_size()

        margin = max(15, int(w * 0.015))
        font_size = max(18, int(h * 0.03))
        font = pygame.font.SysFont("Arial", font_size, bold=True)

        bar_w = max(180, int(w * 0.2))
        bar_h = max(14, int(h * 0.02))

        # ---------------- HP BAR ----------------
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

        # HP
        surface.blit(
            font.render(
                f"HP: {player.hp}/{player.max_hp}",
                True,
                (255, 255, 255)
            ),
            (margin, y)
        )

        y += font_size + 4

        # FLOOR
        surface.blit(
            font.render(
                f"Этаж: {current_floor}",
                True,
                (255, 215, 0)
            ),
            (margin, y)
        )

        y += font_size + 4

        # GOLD
        surface.blit(
            font.render(
                f"Золото: {player.gold}",
                True,
                (255, 215, 0)
            ),
            (margin, y)
        )

        y += font_size + 4

        # ---------------- TIMER ----------------
        time_text = None

        if run_timer is not None:
            time_text = run_timer.get_formatted_time()
        elif score_display:
            time_text = score_display.score_system.get_formatted_time()

        if time_text:
            surface.blit(
                font.render(
                    f"Время: {time_text}",
                    True,
                    (100, 200, 255)
                ),
                (margin, y)
            )
            y += font_size + 4

        # ---------------- SCORE ----------------
        score = None

        if score_manager:
            score = score_manager.score
        elif score_display:
            score = score_display.score_system.score

        if score is not None:
            surface.blit(
                font.render(
                    f"Очки: {score}",
                    True,
                    (255, 215, 0)
                ),
                (margin, y)
            )


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

        resume = self.font_btn.render("Продолжить", True, (255, 255, 255))
        quit_btn = self.font_btn.render("Выйти", True, (255, 255, 255))

        surface.blit(resume, resume.get_rect(center=self.btn_resume.center))
        surface.blit(quit_btn, quit_btn.get_rect(center=self.btn_quit.center))

    def handle_click(self, mouse_pos):
        if self.btn_resume.collidepoint(mouse_pos):
            self.active = False
            return "resume"

        if self.btn_quit.collidepoint(mouse_pos):
            return "quit"

        return None


class StartMenu:
    def __init__(self):
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_btn = pygame.font.SysFont(None, 40)

        self.btn_start = pygame.Rect(0, 0, 260, 56)
        self.btn_quit = pygame.Rect(0, 0, 260, 56)

    def draw(self, surface):
        w, h = surface.get_size()

        surface.fill((10, 10, 20))

        title = self.font_title.render("РОГАЛИК", True, (255, 220, 100))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 140)))

        subtitle = self.font_btn.render("Убей врагов, собери монеты и выходи", True, (220, 220, 220))
        surface.blit(subtitle, subtitle.get_rect(center=(w // 2, h // 2 - 90)))

        self.btn_start.center = (w // 2, h // 2)
        self.btn_quit.center = (w // 2, h // 2 + 90)

        pygame.draw.rect(surface, (80, 80, 120), self.btn_start, border_radius=10)
        pygame.draw.rect(surface, (80, 80, 120), self.btn_quit, border_radius=10)

        start_text = self.font_btn.render("Начать игру", True, (255, 255, 255))
        quit_text = self.font_btn.render("Выйти", True, (255, 255, 255))

        surface.blit(start_text, start_text.get_rect(center=self.btn_start.center))
        surface.blit(quit_text, quit_text.get_rect(center=self.btn_quit.center))

    def handle_click(self, mouse_pos):
        if self.btn_start.collidepoint(mouse_pos):
            return "start"
        if self.btn_quit.collidepoint(mouse_pos):
            return "quit"
        return None


class FinishMenu:
    def __init__(self):
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_btn = pygame.font.SysFont(None, 40)
        self.btn_quit = pygame.Rect(0, 0, 260, 56)

    def draw(self, surface, final_score=None):
        w, h = surface.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((10, 10, 30, 220))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("ВСЕ ЭТАЖИ ПРОЙДЕНЫ", True, (255, 220, 120))
        surface.blit(title, title.get_rect(center=(w // 2, 120)))

        if final_score is not None:
            score_text = self.font_btn.render(
                f"Финальный счёт: {final_score}",
                True,
                (255, 255, 255)
            )
            surface.blit(score_text, score_text.get_rect(center=(w // 2, 210)))

        info_text = self.font_btn.render("Спасибо за игру!", True, (220, 220, 220))
        surface.blit(info_text, info_text.get_rect(center=(w // 2, 260)))

        self.btn_quit.center = (w // 2, h // 2 + 80)
        pygame.draw.rect(surface, (70, 70, 100), self.btn_quit, border_radius=10)

        quit_text = self.font_btn.render("Выйти", True, (255, 255, 255))
        surface.blit(quit_text, quit_text.get_rect(center=self.btn_quit.center))

    def handle_click(self, mouse_pos):
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

    def draw(self, surface, final_score=None, score_manager=None):
        w, h = surface.get_size()

        self.btn_restart.center = (w // 2, h // 2 + 40)
        self.btn_quit.center = (w // 2, h // 2 + 110)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("ВЫ ПОГИБЛИ", True, (200, 0, 0))
        surface.blit(title, title.get_rect(center=(w // 2, 80)))

        # Финальный счёт
        if final_score is not None:
            score_text = self.font_btn.render(
                f"Ваш счёт: {final_score}",
                True,
                (255, 200, 0)
            )
            surface.blit(score_text, score_text.get_rect(center=(w // 2, 140)))

        # TOP-3 лучших результатов
        if score_manager:
            top = score_manager.get_top3()

            y = 200

            title2 = self.font_btn.render(
                "TOP 3 ЗАБЕГОВ",
                True,
                (255, 255, 255)
            )
            surface.blit(title2, title2.get_rect(center=(w // 2, y)))
            y += 40

            for i, score in enumerate(top):
                line = self.font_btn.render(
                    f"{i + 1}. {score}",
                    True,
                    (200, 200, 200)
                )
                surface.blit(line, line.get_rect(center=(w // 2, y)))
                y += 30

        pygame.draw.rect(surface, (50, 50, 50), self.btn_restart, border_radius=8)
        pygame.draw.rect(surface, (50, 50, 50), self.btn_quit, border_radius=8)

        restart = self.font_btn.render("Начать заново", True, (255, 255, 255))
        quit_btn = self.font_btn.render("Выйти", True, (255, 255, 255))

        surface.blit(restart, restart.get_rect(center=self.btn_restart.center))
        surface.blit(quit_btn, quit_btn.get_rect(center=self.btn_quit.center))

    def handle_click(self, mouse_pos):
        if self.btn_restart.collidepoint(mouse_pos):
            return "restart"

        if self.btn_quit.collidepoint(mouse_pos):
            return "quit"

        return None