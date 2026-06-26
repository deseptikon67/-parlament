import sys

import pygame

import map_generator
import settings
import sprites
from card_ui import CardSelectUI
from cards import CardDeck
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
card_ui = CardSelectUI()
deck = CardDeck()

buff_pending_clear = False
paused_from_card_select = False
pending_cards = None


def init_game():
    global buff_pending_clear, paused_from_card_select, pending_cards

    game_map, spawn_x, spawn_y, rooms_data = map_generator.create_map(settings.MAP_COLS, settings.MAP_ROWS)

    all_sprites = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    doors_group = pygame.sprite.Group()

    player = sprites.Player(spawn_x, spawn_y)
    all_sprites.add(player)

    for r in range(len(game_map)):
        for c in range(len(game_map[r])):
            if game_map[r][c] == 1:
                wall = sprites.Wall(c * settings.TILE_SIZE, r * settings.TILE_SIZE)
                all_sprites.add(wall)
                walls_group.add(wall)

    room_manager = RoomManager(rooms_data, settings.TILE_SIZE)

    deck.reset()
    buff_pending_clear = False
    paused_from_card_select = False
    pending_cards = None

    return (
        player,
        all_sprites,
        walls_group,
        enemies,
        player_bullets,
        enemy_bullets,
        doors_group,
        room_manager,
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
) = init_game()

game_state = "playing"
running = True


def draw_world():
    screen.fill(settings.BLACK)

    for wall in walls_group:
        screen.blit(wall.image, camera.apply(wall.rect))

    for door in doors_group:
        screen.blit(door.image, camera.apply(door.rect))

    for enemy in enemies:
        screen.blit(enemy.image, camera.apply(enemy.rect))
        enemy.draw_health_bar(screen, camera)

    for b in player_bullets:
        screen.blit(b.image, camera.apply(b.rect))
    for b in enemy_bullets:
        screen.blit(b.image, camera.apply(b.rect))

    screen.blit(player.image, camera.apply(player.rect))
    hud.draw_player_hp(screen, player)


def clear_card_state():
    global pending_cards, buff_pending_clear, paused_from_card_select
    room_manager.card_event_pending = False
    pending_cards = None
    buff_pending_clear = False
    paused_from_card_select = False
    player.buff_manager.clear()


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
                elif game_state == "card_select":
                    game_state = "paused"
                    pause_menu.active = True
                    paused_from_card_select = True
                elif game_state == "paused":
                    if paused_from_card_select:
                        game_state = "card_select"
                        paused_from_card_select = False
                    else:
                        game_state = "playing"
                    pause_menu.active = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "paused":
                result = pause_menu.handle_click(event.pos)
                if result == "resume":
                    if paused_from_card_select:
                        game_state = "card_select"
                        paused_from_card_select = False
                    else:
                        game_state = "playing"
                    pause_menu.active = False
                elif result == "quit":
                    running = False
            elif game_state == "card_select":
                chosen = card_ui.handle_click(event.pos)
                if chosen:
                    deck.mark_chosen(chosen.id)
                    player.buff_manager.apply_card(chosen)
                    buff_pending_clear = True
                    pending_cards = None
                    game_state = "playing"
            elif game_state == "dead":
                result = death_menu.handle_click(event.pos)
                if result == "restart":
                    (
                        player,
                        all_sprites,
                        walls_group,
                        enemies,
                        player_bullets,
                        enemy_bullets,
                        doors_group,
                        room_manager,
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

        room_manager.update(player, enemies, all_sprites, walls_group, doors_group)

        if room_manager.room_just_cleared and buff_pending_clear:
            player.buff_manager.clear()
            buff_pending_clear = False

        if room_manager.card_event_pending:
            pending_cards = deck.draw(4)
            card_ui.set_cards(pending_cards)
            room_manager.card_event_pending = False
            game_state = "card_select"

        hits = pygame.sprite.groupcollide(player_bullets, enemies, True, False)
        for bullet, hit_list in hits.items():
            damage = int(bullet.damage * player.buff_manager.get_multiplier("damage_dealt"))
            for e in hit_list:
                e.take_damage(damage)

        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for b in hits:
            died = player.take_damage(b.damage)
            if died:
                game_state = "dead"
                death_menu.active = True
                clear_card_state()

        if player.is_dead and pygame.time.get_ticks() - player.death_time > 1333:
            game_state = "dead"
            death_menu.active = True
            clear_card_state()

    if game_state == "card_select":
        card_ui.handle_hover(pygame.mouse.get_pos())

    draw_world()

    if game_state == "card_select":
        card_ui.draw(screen)
    if game_state == "paused":
        pause_menu.draw(screen)
    if game_state == "dead":
        death_menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
