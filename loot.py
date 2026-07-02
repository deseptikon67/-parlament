import random
import pygame
import math

from enemies import BurstRangedEnemy, MeleeEnemy, RangedEnemy


class Coin:

    def __init__(self, x, y):

        self.rect = pygame.Rect(x, y, 16, 16)

    def update(self, player):

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = math.hypot(dx, dy)

        if distance < 150 and distance > 0:

            speed = 3

            self.rect.x += dx / distance * speed
            self.rect.y += dy / distance * speed

    def draw(self, screen, camera):

        pygame.draw.circle(
            screen,
            (255, 215, 0),
            camera.apply(self.rect).center,
            8
        )


class ExpOrb:

    def __init__(self, x, y, amount):

        self.amount = amount
        self.rect = pygame.Rect(x, y, 12, 12)

    def update(self, player):

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = math.hypot(dx, dy)

        if distance < 150 and distance > 0:

            speed = 2

            self.rect.x += dx / distance * speed
            self.rect.y += dy / distance * speed

    def draw(self, screen, camera):

        pygame.draw.circle(
            screen,
            (0, 150, 255),
            camera.apply(self.rect).center,
            6
        )


class LootManager:

    def __init__(self):

        self.coins = []
        self.exp_orbs = []

    def spawn_coins(self, room_rect):

        count = random.randint(2, 5)

        for _ in range(count):

            x = room_rect.centerx + random.randint(-40, 40)
            y = room_rect.centery + random.randint(-40, 40)

            self.coins.append(Coin(x, y))

    def spawn_exp(self, enemy):

        amount = 0

        if isinstance(enemy, BurstRangedEnemy):

            amount = random.randint(1, 2)

        elif isinstance(enemy, (RangedEnemy, MeleeEnemy)):

            amount = random.randint(0, 1)

        if amount <= 0:
            return

        orb = ExpOrb(
            enemy.rect.centerx,
            enemy.rect.centery,
            amount
        )

        self.exp_orbs.append(orb)

    def update_magnet(self, player):

        for coin in self.coins:
            coin.update(player)

        for orb in self.exp_orbs:
            orb.update(player)

    def collect_exp(self, player, room_manager):

        room_cleared = any(room.cleared for room in room_manager.rooms)

        if not room_cleared:
            return

        collected = []

        for orb in self.exp_orbs:

            if player.rect.colliderect(orb.rect):

                player.add_exp(orb.amount)

                collected.append(orb)

        for orb in collected:
            self.exp_orbs.remove(orb)

    def update(self, player):

        collected = 0

        for coin in self.coins[:]:

            if player.rect.colliderect(coin.rect):

                self.coins.remove(coin)

                collected += 1

        return collected

    def draw(self, screen, camera):

        for coin in self.coins:
            coin.draw(screen, camera)

        for orb in self.exp_orbs:
            orb.draw(screen, camera)