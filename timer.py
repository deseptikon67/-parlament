import pygame


class RunTimer:
    def __init__(self):
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.pause_start = None
        self.running = True

    def reset(self):
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.pause_start = None
        self.running = True

    def pause(self):
        if self.running and self.pause_start is None:
            self.pause_start = pygame.time.get_ticks()

    def resume(self):
        if self.pause_start is not None:
            self.paused_time += pygame.time.get_ticks() - self.pause_start
            self.pause_start = None

    def get_time(self):
        if self.pause_start is not None:
            return self.pause_start - self.start_time - self.paused_time
        return pygame.time.get_ticks() - self.start_time - self.paused_time

    def get_formatted_time(self):
        t = max(0, self.get_time() // 1000)
        m = t // 60
        s = t % 60
        return f"{m:02d}:{s:02d}"