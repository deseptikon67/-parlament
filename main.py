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

# --- НОВЫЙ ИМПОРТ ИЗ ВЕТКИ НАПАРНИКА ---
from card_ui import CardSelectUI
from cards import CardDeck

camera = settings.camera

pygame.init()
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("рогалик")
clock = pygame.time.Clock()

hud = HUD()
pause_menu = PauseMenu()
death_menu = DeathMenu()
score_manager = ScoreManager()
run_timer = RunTimer()

# --- ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ КАРТОЧЕК ---
card_ui = CardSelectUI()
card_deck = CardDeck()  # Колода карт

floor_font = pygame.font.SysFont("Arial", 28, bold=True)
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
    if room_manager.all_rooms:
        first_room = room_manager.all_rooms[0]
        return Merchant(
            first_room.pixel_rect.centerx,
            first_room.pixel_rect.top + 60
        )
    return None



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

    for r in range(len(game_map)):
        for c in range(len(game_map[r])):
            if game_map[r][c] == 1:
                wall = sprites.Wall(c * settings.TILE_SIZE, r * settings.TILE_SIZE)
                all_sprites.add(wall)
                walls_group.add(wall)

    room_manager = RoomManager(rooms_data, settings.TILE_SIZE)
    room_manager.score_given = False

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
        loot_manager,
    )


# --- ФУНКЦИЯ "ПЕРЕВОДЧИК" ДЛЯ ПРИМЕНЕНИЯ И СБРОСА СТАТОВ ---
def apply_card_stat(player_obj, card_stat_name, multiplier, revert=False):
    # Если мы отменяем старую карту (revert=True), мы ДЕЛИМ на множитель (откатываем)
    actual_mult = (1.0 / multiplier) if revert else multiplier
    action_text = "[-] СБРОС" if revert else "[+] ПРИМЕНЕНИЕ"

    # 1. УРОН
    if card_stat_name == "damage_dealt":
        player_obj.bullet_damage = player_obj.bullet_damage * actual_mult
        print(f"{action_text} {card_stat_name}: Урон пули стал {player_obj.bullet_damage:.1f}")

    # 2. СКОРОСТЬ
    elif card_stat_name == "move_speed":
        player_obj.base_speed = player_obj.base_speed * actual_mult
        print(f"{action_text} {card_stat_name}: Скорость стала {player_obj.base_speed:.1f}")

    # 3. ПЕРЕЗАРЯДКА
    elif card_stat_name == "shoot_cooldown":
        player_obj.base_shoot_cooldown = player_obj.base_shoot_cooldown * actual_mult
        print(f"{action_text} {card_stat_name}: Кулдаун стрельбы стал {player_obj.base_shoot_cooldown:.1f}")

    # 4. ВХОДЯЩИЙ УРОН (ЗАЩИТА)
    elif card_stat_name == "damage_taken":
        bm = player_obj.buff_manager
        d = getattr(bm, "multipliers", getattr(bm, "_multipliers", {}))
        current = d.get(card_stat_name, 1.0)
        d[card_stat_name] = current * actual_mult
        print(f"{action_text} {card_stat_name}: Множитель уязвимости стал {d[card_stat_name]:.2f}")


# -----------------------------------------------------------------


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
            if game_state == "card_select":
                selected_card = card_ui.handle_click(event.pos)
                if selected_card is not None:
                    # Убираем карту из колоды
                    card_deck.mark_chosen(selected_card.id)

                    # --- ШАГ 1: ОТМЕНЯЕМ СТАРУЮ КАРТУ (ЕСЛИ ОНА БЫЛА) ---
                    if hasattr(player, "active_card") and player.active_card is not None:
                        old_card = player.active_card
                        print(f"\n--- ОТКАТ СТАРОЙ КАРТЫ: {old_card.name} ---")
                        apply_card_stat(player, old_card.buff_stat, old_card.buff_value, revert=True)
                        apply_card_stat(player, old_card.debuff_stat, old_card.debuff_value, revert=True)

                    # --- ШАГ 2: ПРИМЕНЯЕМ НОВУЮ КАРТУ ---
                    print(f"\n--- ВЫБРАНА НОВАЯ КАРТА: {selected_card.name} ---")
                    apply_card_stat(player, selected_card.buff_stat, selected_card.buff_value, revert=False)
                    apply_card_stat(player, selected_card.debuff_stat, selected_card.debuff_value, revert=False)

                    # --- ШАГ 3: ЗАПОМИНАЕМ ЕЁ КАК АКТИВНУЮ ---
                    player.active_card = selected_card

                    # Возвращаемся в игру
                    game_state = "playing"

            elif merchant and game_state == "playing":
                merchant.handle_click(player, event.pos)

            elif game_state == "paused":
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
                    if hasattr(player, "gold"):
                        player.gold = 0

                    merchant = spawn_merchant(room_manager)
                    game_state = "playing"
                    death_menu.active = False
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

        # ЛОВИМ СИГНАЛ ЗАЧИСТКИ КОМНАТЫ
        if room_manager.card_event_pending:
            drawn_cards = card_deck.draw(3)
            card_ui.set_cards(drawn_cards)
            game_state = "card_select"
            room_manager.card_event_pending = False

        loot_manager.update_magnet(player)

        collected_coins = loot_manager.update(player)
        if hasattr(player, "gold"):
            player.gold += collected_coins

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

    if game_state == "card_select":
        card_ui.handle_hover(pygame.mouse.get_pos())

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