import pygame
import time


class ScoreSystem:
    """Система подсчета очков с таймером"""
    
    def __init__(self):
        self.score = 0
        self.start_time = time.time()
        self.kill_points = 10        # очки за убийство
        self.room_clear_points = 50  # очки за зачистку комнаты
        self.coin_points = 1         # очки за монету
        
    def add_kill_points(self):
        """Добавить очки за убийство (1 убийство = 10 очков)"""
        self.score += self.kill_points
        return self.score
    
    def add_room_clear_points(self):
        """Добавить очки за зачистку комнаты (50 очков)"""
        self.score += self.room_clear_points
        return self.score
    
    def add_coin_points(self, count=1):
        """Добавить очки за подбор монет (1 монета = 1 очко)"""
        self.score += self.coin_points * count
        return self.score
    
    def get_elapsed_time(self):
        """Получить прошедшее время в секундах"""
        return int(time.time() - self.start_time)
    
    def get_formatted_time(self):
        """Получить форматированное время (ММ:СС)"""
        elapsed = self.get_elapsed_time()
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def reset(self):
        """Сбросить счетчик очков и таймер"""
        self.score = 0
        self.start_time = time.time()


class ScoreDisplay:
    """Отображение очков и таймера на экране"""
    
    def __init__(self):
        self.score_system = ScoreSystem()
    
    def draw(self, surface, x, y):
        """Рисовать таймер и очки на экране
        
        Args:
            surface: pygame поверхность для рисования
            x: координата X
            y: координата Y
        """
        w, h = surface.get_size()
        font_size = max(18, int(h * 0.03))
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        
        # Таймер
        time_text = font.render(
            f"Время: {self.score_system.get_formatted_time()}",
            True,
            (100, 200, 255)
        )
        surface.blit(time_text, (x, y))
        
        # Очки
        score_text = font.render(
            f"Очки: {self.score_system.score}",
            True,
            (255, 215, 0)
        )
        surface.blit(score_text, (x, y + font_size + 8))
    
    def add_kill_points(self):
        """Добавить очки за убийство"""
        return self.score_system.add_kill_points()
    
    def add_room_clear_points(self):
        """Добавить очки за зачистку комнаты"""
        return self.score_system.add_room_clear_points()
    
    def add_coin_points(self, count=1):
        """Добавить очки за подбор монет"""
        return self.score_system.add_coin_points(count)
    
    def reset(self):
        """Сбросить счетчик"""
        self.score_system.reset()
    
    def get_score_data(self):
        """Получить данные об очках и времени для отчета"""
        return {
            'score': self.score_system.score,
            'time': self.score_system.get_formatted_time(),
            'elapsed_seconds': self.score_system.get_elapsed_time()
        }
