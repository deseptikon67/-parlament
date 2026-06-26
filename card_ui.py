import pygame

import settings
from cards import Card

GOLD = (212, 175, 55)
GREEN = (80, 220, 100)
RED = (220, 80, 80)
CARD_BG = (30, 20, 50)
CARD_HOVER = (50, 40, 80)

def fit_font(text: str, max_width: int, base_size: int, font_name=None, bold=False, min_size=12):
    """Подбирает максимальный размер шрифта, при котором text влезает в max_width."""
    size = base_size
    while size > min_size:
        font = pygame.font.SysFont(font_name, size, bold=bold)
        if font.size(text)[0] <= max_width:
            return font
        size -= 1
    return pygame.font.SysFont(font_name, min_size, bold=bold)

class CardSelectUI:
    def __init__(self):
        self.cards: list[Card] = []
        self.card_rects: list[pygame.Rect] = []
        self.hovered_index: int | None = None
        self.font_title = pygame.font.SysFont(None, 48)
        self.font_name = pygame.font.SysFont(None, 28)
        self.font_suit = pygame.font.SysFont(None, 56)
        self.font_desc = pygame.font.SysFont(None, 20)

    def set_cards(self, cards: list[Card]):
        self.cards = list(cards)
        self.hovered_index = None
        self._layout()

    def _layout(self):
        n = len(self.cards)
        if n == 0:
            self.card_rects = []
            return
        card_w, card_h = 150, 220
        gap = 20
        total_w = n * card_w + (n - 1) * gap
        start_x = (settings.WIDTH - total_w) // 2
        y = (settings.HEIGHT - card_h) // 2 + 20
        self.card_rects = []
        for i in range(n):
            x = start_x + i * (card_w + gap)
            self.card_rects.append(pygame.Rect(x, y, card_w, card_h))

    def handle_hover(self, mouse_pos):
        self.hovered_index = None
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(mouse_pos):
                self.hovered_index = i
                break

    def handle_click(self, mouse_pos) -> Card | None:
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(mouse_pos):
                return self.cards[i]
        return None

    def draw(self, surface):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("Выберите карту", True, GOLD)
        surface.blit(title, title.get_rect(center=(settings.WIDTH // 2, 60)))

        for i, (card, rect) in enumerate(zip(self.cards, self.card_rects)):
            hovered = i == self.hovered_index
            bg = CARD_HOVER if hovered else CARD_BG
            border = 4 if hovered else 2
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            pygame.draw.rect(surface, GOLD, rect, border, border_radius=10)

            suit_surf = self.font_suit.render(card.suit, True, GOLD)
            surface.blit(suit_surf, suit_surf.get_rect(center=(rect.centerx, rect.top + 40)))

            text_max_w = rect.width - 16  # отступ по 8px с каждой стороны карты

            name_font = fit_font(card.name, text_max_w, base_size=28, bold=True)
            name_surf = name_font.render(card.name, True, (255, 255, 255))
            surface.blit(name_surf, name_surf.get_rect(center=(rect.centerx, rect.top + 90)))

            buff_font = fit_font(card.buff_text, text_max_w, base_size=20)
            buff_surf = buff_font.render(card.buff_text, True, GREEN)
            surface.blit(buff_surf, buff_surf.get_rect(center=(rect.centerx, rect.top + 140)))

            debuff_font = fit_font(card.debuff_text, text_max_w, base_size=20)
            debuff_surf = debuff_font.render(card.debuff_text, True, RED)
            surface.blit(debuff_surf, debuff_surf.get_rect(center=(rect.centerx, rect.top + 170)))