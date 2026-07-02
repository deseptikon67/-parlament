import pygame
import os
import settings
from cards import Card

GOLD = (212, 175, 55)
GREEN = (80, 220, 100)
RED = (220, 80, 80)
CARD_BG = (30, 20, 50)
CARD_HOVER = (50, 40, 80)

def fit_font(text: str, max_width: int, base_size: int, font_name=None, bold=False, min_size=12):
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
        
        self.card_sprites = {}
        self.load_cards()

    def load_cards(self):
        """Загружает картинки из assets/cards/"""
        card_ids = [
            "ace_spades", "king_hearts", "queen_diamonds", "jack_clubs",
            "va_bank", "double_stake", "bluff", "all_in",
            "lucky_seven", "house_edge", "hot_streak", "cold_read"
        ]
        
        card_size = (160, 240)

        for cid in card_ids:
            path_png = os.path.join("assets", "cards", f"{cid}.png")
            path_jpg = os.path.join("assets", "cards", f"{cid}.jpg")
            
            loaded_img = None
            if os.path.exists(path_png):
                loaded_img = pygame.image.load(path_png).convert_alpha()
            elif os.path.exists(path_jpg):
                loaded_img = pygame.image.load(path_jpg).convert_alpha()
                
            if loaded_img:
                scaled_img = pygame.transform.smoothscale(loaded_img, card_size)
                self.card_sprites[cid] = scaled_img

    def set_cards(self, cards: list[Card]):
        self.cards = list(cards)
        self.hovered_index = None
        self._layout()

    def _layout(self):
        n = len(self.cards)
        if n == 0:
            self.card_rects = []
            return
        
        card_w, card_h = 160, 240
        gap = 30
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
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("ВЫБЕРИТЕ УЛУЧШЕНИЕ", True, GOLD)
        surface.blit(title, title.get_rect(center=(settings.WIDTH // 2, 60)))

        for i, (card, rect) in enumerate(zip(self.cards, self.card_rects)):
            hovered = i == self.hovered_index
            
            # Если картинка успешно загрузилась из папки
            if card.id in self.card_sprites:
                surface.blit(self.card_sprites[card.id], rect.topleft)
                if hovered:
                    pygame.draw.rect(surface, GOLD, rect, 4, border_radius=8)
                    
            # Резервный вариант, если картинки нет (Рисуем плотный фон и текст)
            else:
                bg = CARD_HOVER if hovered else CARD_BG
                border = 4 if hovered else 2
                
                # Рисуем плотный непрозрачный фон
                pygame.draw.rect(surface, bg, rect, border_radius=10)
                pygame.draw.rect(surface, GOLD, rect, border, border_radius=10)

                text_max_w = rect.width - 16

                name_font = fit_font(card.name, text_max_w, base_size=28, bold=True)
                name_surf = name_font.render(card.name, True, (255, 255, 255))
                surface.blit(name_surf, name_surf.get_rect(center=(rect.centerx, rect.top + 90)))

                if hasattr(card, 'buff_text') and card.buff_text:
                    buff_font = fit_font(card.buff_text, text_max_w, base_size=20)
                    buff_surf = buff_font.render(card.buff_text, True, GREEN)
                    surface.blit(buff_surf, buff_surf.get_rect(center=(rect.centerx, rect.top + 140)))

                if hasattr(card, 'debuff_text') and card.debuff_text:
                    debuff_font = fit_font(card.debuff_text, text_max_w, base_size=20)
                    debuff_surf = debuff_font.render(card.debuff_text, True, RED)
                    surface.blit(debuff_surf, debuff_surf.get_rect(center=(rect.centerx, rect.top + 170)))