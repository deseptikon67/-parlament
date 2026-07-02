import sys

import pygame

import map_generator
import settings
import sprites
from enemies import EnemyBullet, MeleeEnemy, PlayerBullet, RangedEnemy
from hud import DeathMenu, HUD, PauseMenu
from room_manager import RoomManager
from settings import HEIGHT, WIDTH, camera

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("рогалик")
clock = pygame.time.Clock()

hud = HUD()
pause_menu = PauseMenu()
death_menu = DeathMenu()

floor_font = pygame.font.SysFont("Arial", 28, bold=True)
current_floor = 1


class Elevator(pygame.sprite.Sprite):

    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((100, 100, 100))
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, size, size), 4)
        pygame.draw.rect(
            self.image,
            (75, 75, 75),
            (size // 4, size // 4, size // 2, size // 2),
            2,
        )
        self.rect = self.image.get_rect(center=(x, y))


def init_game(existing_player=None):
    (
        game_map,
        spawn_x,
        spawn_y,
        exit_x,
        exit_y,
        rooms_data,
    ) = map_generator.create_map(settings.MAP_COLS, settings.MAP_ROWS)

    all_sprites = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    doors_group = pygame.sprite.Group()
    exit_group = pygame.sprite.Group()

    if existing_player is not None:
        player = existing_player
        player.rect.x = spawn_x * settings.TILE_SIZE
        player.rect.y = spawn_y * settings.TILE_SIZE
        if hasattr(player, "x"):
            player.x = player.rect.x
        if hasattr(player, "y"):
            player.y = player.rect.y
    else:
        player = sprites.Player(spawn_x, spawn_y)

    all_sprites.add(player)

    # --- НАДЕЖНЫЙ ФИКС ЛИФТА (Ищет комнату выхода) ---
    exit_room_data = next((r for r in rooms_data if isinstance(r, dict) and r.get("is_exit")), None)

    if exit_room_data and "cx" in exit_room_data and "cy" in exit_room_data:
        pixel_cx = exit_room_data["cx"] * settings.TILE_SIZE + settings.TILE_SIZE // 2
        pixel_cy = exit_room_data["cy"] * settings.TILE_SIZE + settings.TILE_SIZE // 2
    else:
        if exit_x == spawn_x and exit_y == spawn_y:
            exit_x = settings.MAP_COLS - 4
            exit_y = settings.MAP_ROWS - 4
        pixel_cx = exit_x * settings.TILE_SIZE + settings.TILE_SIZE // 2
        pixel_cy = exit_y * settings.TILE_SIZE + settings.TILE_SIZE // 2

    elevator = Elevator(pixel_cx, pixel_cy, settings.TILE_SIZE * 2)
    exit_group.add(elevator)
    # -------------------------------------------------

    for r in range(len(game_map)):
        for c in range(len(game_map[r])):
            if game_map[r][c] == 1:
                wall = sprites.Wall(
                    c * settings.TILE_SIZE, r * settings.TILE_SIZE
                )
                all_sprites.add(wall)
                walls_group.add(wall)

    room_manager = RoomManager(rooms_data, settings.TILE_SIZE)

    if hasattr(room_manager, "combat_rooms"):
        cleaned_rooms = []
        for r in room_manager.combat_rooms:
            is_s = (
                    getattr(r, "is_spawn", False)
                    or (isinstance(r, dict) and r.get("is_spawn"))
                    or False
            )
            is_e = (
                    getattr(r, "is_exit", False)
                    or (isinstance(r, dict) and r.get("is_exit"))
                    or False
            )
            if hasattr(r, "room_data") and isinstance(r.room_data, dict):
                is_s = is_s or r.room_data.get("is_spawn")
                is_e = is_e or r.room_data.get("is_exit")
            if hasattr(r, "type"):
                is_s = is_s or (getattr(r, "type") == "spawn")
                is_e = is_e or (getattr(r, "type") == "exit")

            if not is_s and not is_e:
                cleaned_rooms.append(r)
        room_manager.combat_rooms = cleaned_rooms

    return (
        player,
        all_sprites,
        walls_group,
        enemies,
        player_bullets,
        enemy_bullets,
        doors_group,
        room_manager,
        exit_group,
    )


# Первый запуск
(
    player,
    all_sprites,
    walls_group,
    enemies,
    player_bullets,
    enemy_bullets,
    doors_group,
    room_manager,
    exit_group,
) = init_game()

game_state = "playing"
running = True

while running:
    clock.tick(settings.FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "playing":
                    game_state = "paused"
                    pause_menu.active = True
                elif game_state == "paused":
                    game_state = "playing"
                    pause_menu.active = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "paused":
                result = pause_menu.handle_click(event.pos)
                if result == "resume":
                    game_state = "playing"
                    pause_menu.active = False
                elif result == "quit":
                    running = False
            elif game_state == "dead":
                result = death_menu.handle_click(event.pos)
                if result == "restart":
                    current_floor = 1
                    (
                        player,
                        all_sprites,
                        walls_group,
                        enemies,
                        player_bullets,
                        enemy_bullets,
                        doors_group,
                        room_manager,
                        exit_group,
                    ) = init_game()
                    game_state = "playing"
                    death_menu.active = False
                elif result == "quit":
                    running = False

    if game_state == "playing":
        camera.update(player, WIDTH, HEIGHT)
        player.update(walls_group, player_bullets)

        for enemy in enemies:
            enemy.update(player, walls_group, enemy_bullets)

        for _ in range(2):
            for enemy in enemies:
                enemy.resolve_peer_collisions(enemies)

        player_bullets.update(walls_group)
        enemy_bullets.update(walls_group)

        room_manager.update(
            player, enemies, all_sprites, walls_group, doors_group
        )

        all_combat_cleared = (
            all(room.cleared for room in room_manager.combat_rooms)
            if room_manager.combat_rooms
            else True
        )

        if all_combat_cleared and pygame.sprite.spritecollide(
                player, exit_group, False
        ):
            current_floor += 1
            (
                player,
                all_sprites,
                walls_group,
                enemies,
                player_bullets,
                enemy_bullets,
                doors_group,
                room_manager,
                exit_group,
            ) = init_game(existing_player=player)

        hits = pygame.sprite.groupcollide(player_bullets, enemies, True, False)
        for bullet, hit_list in hits.items():
            for e in hit_list:
                e.take_damage(bullet.damage)

        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for b in hits:
            died = player.take_damage(b.damage)
            if died:
                game_state = "dead"
                death_menu.active = True

        if player.is_dead and pygame.time.get_ticks() - player.death_time > 1333:
            game_state = "dead"
            death_menu.active = True

    screen.fill(settings.BLACK)

    for wall in walls_group:
        screen.blit(wall.image, camera.apply(wall.rect))
    for door in doors_group:
        screen.blit(door.image, camera.apply(door.rect))
    for ev in exit_group:
        screen.blit(ev.image, camera.apply(ev.rect))
    for enemy in enemies:
        screen.blit(enemy.image, camera.apply(enemy.rect))
        enemy.draw_health_bar(screen, camera)

    for b in player_bullets:
        screen.blit(b.image, camera.apply(b.rect))
    for b in enemy_bullets:
        screen.blit(b.image, camera.apply(b.rect))

    screen.blit(player.image, camera.apply(player.rect))

    # Используем старый метод отрисовки HP, чтобы не ломать проект до мерджа
    hud.draw_player_hp(screen, player)

    floor_text = floor_font.render(
        f"Этаж: {current_floor}", True, (255, 215, 0)
    )
    screen.blit(floor_text, (20, 60))

    if game_state == "paused":
        pause_menu.draw(screen)
    if game_state == "dead":
        death_menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()