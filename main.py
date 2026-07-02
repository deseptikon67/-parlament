import sys
import pygame

import map_generator
import settings
import sprites
from enemies import EnemyBullet, MeleeEnemy, PlayerBullet, RangedEnemy
from hud import HUD, PauseMenu, DeathMenu
from loot import LootManager
from room_manager import RoomManager

camera = settings.camera
from merchant import Merchant
from score import ScoreManager
from timer import RunTimer

pygame.init()
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("рогалик")
clock = pygame.time.Clock()

hud = HUD()
pause_menu = PauseMenu()
death_menu = DeathMenu()
score_manager = ScoreManager()
run_timer = RunTimer()

current_floor = 1


class Elevator(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((100, 100, 100))
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, size, size), 4)
        pygame.draw.rect(self.image, (75, 75, 75),
                         (size // 4, size // 4, size // 2, size // 2), 2)
        self.rect = self.image.get_rect(center=(x, y))


def spawn_merchant(room_manager):
    if not room_manager or not room_manager.all_rooms:
        return None

    first_room = room_manager.all_rooms[0]

    return Merchant(
        first_room.pixel_rect.centerx,
        first_room.pixel_rect.top + 60
    )


def init_game(existing_player=None):
    game_map, spawn_x, spawn_y, rooms_data = map_generator.create_map(
        settings.MAP_COLS, settings.MAP_ROWS
    )

    all_sprites = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    doors_group = pygame.sprite.Group()
    exit_group = pygame.sprite.Group()

    loot_manager = LootManager()

    if existing_player:
        player = existing_player
        player.rect.x = spawn_x * settings.TILE_SIZE
        player.rect.y = spawn_y * settings.TILE_SIZE
        player.x = player.rect.x
        player.y = player.rect.y
    else:
        player = sprites.Player(spawn_x, spawn_y)

    all_sprites.add(player)

    exit_room = next((r for r in rooms_data if r.get("is_exit")), None)
    if exit_room:
        cx = exit_room["cx"] * settings.TILE_SIZE + settings.TILE_SIZE // 2
        cy = exit_room["cy"] * settings.TILE_SIZE + settings.TILE_SIZE // 2
        exit_group.add(Elevator(cx, cy, settings.TILE_SIZE * 2))

    for r in range(len(game_map)):
        for c in range(len(game_map[r])):
            if game_map[r][c] == 1:
                wall = sprites.Wall(c * settings.TILE_SIZE, r * settings.TILE_SIZE)
                all_sprites.add(wall)
                walls_group.add(wall)

    room_manager = RoomManager(rooms_data, settings.TILE_SIZE)
    room_manager.score_given = False

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
        loot_manager,
    )


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
    loot_manager,
) = init_game()

merchant = spawn_merchant(room_manager)

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
                elif result == "quit":
                    running = False

            elif game_state == "dead":
                result = death_menu.handle_click(event.pos)

                if result == "restart":
                    try:
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
                            loot_manager,
                        ) = init_game()

                        score_manager.reset()
                        run_timer.reset()

                        merchant = spawn_merchant(room_manager)

                        game_state = "playing"
                        death_menu.active = False

                    except Exception as e:
                        print("RESTART ERROR:", e)

                elif result == "quit":
                    running = False

    # ================= GAME =================
    if game_state == "playing":
        run_timer.resume()

        if merchant:
            merchant.update(player)

        camera.update(player, screen.get_width(), screen.get_height())
        player.update(walls_group, player_bullets)

        for enemy in enemies:
            enemy.update(player, walls_group, enemy_bullets)

        for _ in range(2):
            for enemy in enemies:
                enemy.resolve_peer_collisions(enemies)

        player_bullets.update(walls_group)
        enemy_bullets.update(walls_group)

        room_manager.update(player, enemies, all_sprites,
                            walls_group, doors_group, loot_manager)

        loot_manager.update_magnet(player)
        collected = loot_manager.update(player)

        if collected:
            for _ in range(collected):
                score_manager.coin()

        player.gold += collected
        loot_manager.collect_exp(player, room_manager)

        hits = pygame.sprite.groupcollide(player_bullets, enemies, True, False)
        for bullet, hit_list in hits.items():
            for enemy in hit_list:
                if enemy.take_damage(bullet.damage):
                    score_manager.kill()
                    loot_manager.spawn_exp(enemy)
                    enemy.kill()

        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for b in hits:
            if player.take_damage(b.damage):
                score_manager.save_run()
                death_menu.final_score = score_manager.score
                game_state = "dead"
                death_menu.active = True

        if player.is_dead:
            score_manager.save_run()
            death_menu.final_score = score_manager.score
            game_state = "dead"
            death_menu.active = True

        all_cleared = all(r.cleared for r in room_manager.combat_rooms)

        if all_cleared and pygame.sprite.spritecollide(player, exit_group, False):
            if not room_manager.score_given:
                score_manager.room_clear()
                room_manager.score_given = True

        if all_cleared and pygame.sprite.spritecollide(player, exit_group, False):
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
                loot_manager,
            ) = init_game(existing_player=player)

            merchant = spawn_merchant(room_manager)

    # ================= RENDER =================
    screen.fill(settings.BLACK)

    for wall in walls_group:
        screen.blit(wall.image, camera.apply(wall.rect))

    for door in doors_group:
        screen.blit(door.image, camera.apply(door.rect))

    for ev in exit_group:
        screen.blit(ev.image, camera.apply(ev.rect))

    loot_manager.draw(screen, camera)

    for enemy in enemies:
        screen.blit(enemy.image, camera.apply(enemy.rect))
        enemy.draw_health_bar(screen, camera)

    for b in player_bullets:
        screen.blit(b.image, camera.apply(b.rect))

    for b in enemy_bullets:
        screen.blit(b.image, camera.apply(b.rect))

    screen.blit(player.image, camera.apply(player.rect))

    if merchant:
        merchant.draw(screen, camera)

    hud.draw(
        screen,
        player,
        current_floor,
        score_manager=score_manager,
        run_timer=run_timer
    )

    if game_state == "paused":
        pause_menu.draw(screen)
        run_timer.pause()

    if game_state == "dead":
        death_menu.draw(screen, score_manager.score, score_manager)
        run_timer.pause()

    pygame.display.flip()

pygame.quit()
sys.exit()