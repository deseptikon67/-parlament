import sys
import array
import math
import pygame
import map_generator
import settings
import sprites
from enemies import EnemyBullet, MeleeEnemy, PlayerBullet, RangedEnemy
from hud import HUD, PauseMenu, DeathMenu, StartMenu, FinishMenu
from loot import LootManager
from room_manager import RoomManager
from merchant import Merchant

# --- ИМПОРТ ИЗ ВЕТКИ НАПАРНИКА ---
from card_ui import CardSelectUI
from cards import CardDeck

# --- ИМПОРТ СИСТЕМЫ СЧЕТА И ТАЙМЕРА ---
from score import ScoreDisplay

camera = settings.camera

pygame.init()

pygame.mixer.music.load("assets/theme.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
death_sound = pygame.mixer.Sound("assets/lose.mp3")
death_sound.set_volume(0.8)
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
except pygame.error:
    pass

# Флаги FULLSCREEN и SCALED сделают игру полноэкранной и аккуратно растянут её
screen = pygame.display.set_mode(
    (settings.WIDTH, settings.HEIGHT), 
    pygame.FULLSCREEN | pygame.SCALED
)
pygame.display.set_caption("рогалик")
clock = pygame.time.Clock()

hud = HUD()
pause_menu = PauseMenu()
death_menu = DeathMenu()
start_menu = StartMenu()


def make_sound(freq, duration=0.12, volume=0.3, sample_rate=22050):
    length = int(sample_rate * duration)
    samples = array.array('h', [
        int(32767 * volume * math.sin(2 * math.pi * freq * i / sample_rate) * (1.0 - i / length))
        for i in range(length)
    ])
    return pygame.mixer.Sound(buffer=samples)

shoot_sound = None
if pygame.mixer.get_init():
    try:
        shoot_sound = make_sound(880, duration=0.08, volume=0.35)
    except Exception:
        shoot_sound = None
finish_menu = FinishMenu()

score_display = ScoreDisplay()
score_manager = score_display.score_system  
run_timer = score_display.score_system      

# Динамическая заглушка для рекордов, если их нет в score.py
if not hasattr(score_manager, 'top3_scores'):
    score_manager.top3_scores = []

if not hasattr(score_manager, 'get_top3'):
    def get_top3_dynamic():
        return sorted(score_manager.top3_scores, reverse=True)[:3]
    score_manager.get_top3 = get_top3_dynamic

if not hasattr(score_manager, 'add_to_top'):
    def add_to_top_dynamic(score_value):
        score_manager.top3_scores.append(score_value)
    score_manager.add_to_top = add_to_top_dynamic


# --- ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ КАРТОЧЕК ---
card_ui = CardSelectUI()
card_deck = CardDeck()  

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


def spawn_merchant(room_manager):
    if room_manager.all_rooms:
        first_room = room_manager.all_rooms[0]
        return Merchant(
            first_room.pixel_rect.centerx + 170,
            first_room.pixel_rect.top + 200
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

    if shoot_sound is not None:
        player.shoot_sound = shoot_sound

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

    # --- ОПТИМИЗАЦИЯ ПОЛА (БЕЗ ГОСТИНГА) ---
    map_width = len(game_map[0]) * settings.TILE_SIZE
    map_height = len(game_map) * settings.TILE_SIZE
    floor_background = pygame.Surface((map_width, map_height))

    temp_floor = sprites.Floor(0, 0, size=settings.TILE_SIZE)

    for r in range(len(game_map)):
        for c in range(len(game_map[r])):
            floor_background.blit(temp_floor.image, (c * settings.TILE_SIZE, r * settings.TILE_SIZE))
            if game_map[r][c] == 1:
                wall = sprites.Wall(
                    c * settings.TILE_SIZE,
                    r * settings.TILE_SIZE,
                    size=settings.TILE_SIZE,
                )
                all_sprites.add(wall)
                walls_group.add(wall)

    room_manager = RoomManager(rooms_data, settings.TILE_SIZE)

    # --- ЖЕЛЕЗОБЕТОННАЯ ГЕОМЕТРИЧЕСКАЯ ФИЛЬТРАЦИЯ КОМНАТ ---
    if hasattr(room_manager, "combat_rooms"):
        cleaned_rooms = []
        spawn_pixel_x = spawn_x * settings.TILE_SIZE + settings.TILE_SIZE // 2
        spawn_pixel_y = spawn_y * settings.TILE_SIZE + settings.TILE_SIZE // 2

        for r in room_manager.combat_rooms:
            is_s = False
            is_e = False

            # 1. Проверка по физическому расположению (Координатная защита)
            if hasattr(r, "pixel_rect") and r.pixel_rect is not None:
                if hasattr(r.pixel_rect, "collidepoint"):
                    if r.pixel_rect.collidepoint(spawn_pixel_x, spawn_pixel_y):
                        is_s = True
                    if r.pixel_rect.collidepoint(pixel_cx, pixel_cy):
                        is_e = True
                else:
                    # Резервный расчет, если pixel_rect — это не Rect, а кастомный объект
                    rx = getattr(r.pixel_rect, "x", 0)
                    ry = getattr(r.pixel_rect, "y", 0)
                    rw = getattr(r.pixel_rect, "width", getattr(r.pixel_rect, "w", 0))
                    rh = getattr(r.pixel_rect, "height", getattr(r.pixel_rect, "h", 0))
                    if rx <= spawn_pixel_x < rx + rw and ry <= spawn_pixel_y < ry + rh:
                        is_s = True
                    if rx <= pixel_cx < rx + rw and ry <= pixel_cy < ry + rh:
                        is_e = True

            # 2. Дополнительная проверка по текстовым свойствам (на всякий случай)
            if hasattr(r, "is_spawn") and r.is_spawn: is_s = True
            if hasattr(r, "is_exit") and r.is_exit: is_e = True
            if hasattr(r, "type"):
                if r.type == "spawn": is_s = True
                if r.type == "exit": is_e = True

            if hasattr(r, "room_data") and isinstance(r.room_data, dict):
                if r.room_data.get("is_spawn") or r.room_data.get("type") == "spawn": is_s = True
                if r.room_data.get("is_exit") or r.room_data.get("type") == "exit": is_e = True

            if isinstance(r, dict):
                if r.get("is_spawn") or r.get("type") == "spawn": is_s = True
                if r.get("is_exit") or r.get("type") == "exit": is_e = True

            # 3. Полностью исключаем магазины и сокровищницы из боевых комнат
            is_safe_type = False
            if hasattr(r, "type") and r.type in ["shop", "treasure"]: is_safe_type = True
            if hasattr(r, "room_data") and isinstance(r.room_data, dict) and r.room_data.get("type") in ["shop", "treasure"]: is_safe_type = True
            if isinstance(r, dict) and r.get("type") in ["shop", "treasure"]: is_safe_type = True

            # Если комната не спавн, не лифт и не мирная зона — отправляем на спавн врагов
            if not is_s and not is_e and not is_safe_type:
                cleaned_rooms.append(r)
                
        room_manager.combat_rooms = cleaned_rooms

    return (
        player,
        floor_background,
        walls_group,
        enemies,
        player_bullets,
        enemy_bullets,
        doors_group,
        room_manager,
        exit_group,
        loot_manager,
    )


def apply_card_stat(player_obj, card_stat_name, multiplier, revert=False):
    actual_mult = (1.0 / multiplier) if revert else multiplier
    action_text = "[-] СБРОС" if revert else "[+] ПРИМЕНЕНИЕ"

    if card_stat_name == "damage_dealt":
        player_obj.bullet_damage = player_obj.bullet_damage * actual_mult
        print(f"{action_text} {card_stat_name}: Урон пули стал {player_obj.bullet_damage:.1f}")

    elif card_stat_name == "move_speed":
        player_obj.base_speed = player_obj.base_speed * actual_mult
        print(f"{action_text} {card_stat_name}: Скорость стала {player_obj.base_speed:.1f}")

    elif card_stat_name == "shoot_cooldown":
        player_obj.base_shoot_cooldown = player_obj.base_shoot_cooldown * actual_mult
        print(f"{action_text} {card_stat_name}: Кулдаун стрельбы стал {player_obj.base_shoot_cooldown:.1f}")
        
    elif card_stat_name == "damage_taken":
        bm = player_obj.buff_manager
        d = getattr(bm, "multipliers", getattr(bm, "_multipliers", {}))
        current = d.get(card_stat_name, 1.0)
        d[card_stat_name] = current * actual_mult
        print(f"{action_text} {card_stat_name}: Множитель уязвимости стал {d[card_stat_name]:.2f}")


# -----------------------------------------------------------------

(
    player,
    floor_background,
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
game_state = "start"
running = True
final_score_saved = 0  

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
                    pygame.mixer.music.pause()

                elif game_state == "paused":
                    game_state = "playing"
                    pause_menu.active = False
                    pygame.mixer.music.unpause()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "card_select":
                selected_card = card_ui.handle_click(event.pos)
                if selected_card is not None:
                    card_deck.mark_chosen(selected_card.id)

                    if hasattr(player, "active_card") and player.active_card is not None:
                        old_card = player.active_card
                        print(f"\n--- ОТКАТ СТАРОЙ КАРТЫ: {old_card.name} ---")
                        apply_card_stat(player, old_card.buff_stat, old_card.buff_value, revert=True)
                        apply_card_stat(player, old_card.debuff_stat, old_card.debuff_value, revert=True)

                    print(f"\n--- ВЫБРАНА НОВАЯ КАРТА: {selected_card.name} ---")
                    apply_card_stat(player, selected_card.buff_stat, selected_card.buff_value, revert=False)
                    apply_card_stat(player, selected_card.debuff_stat, selected_card.debuff_value, revert=False)

                    player.active_card = selected_card
                    game_state = "playing"

            elif merchant and game_state == "playing":
                merchant.handle_click(player, event.pos)

            elif game_state == "paused":
                result = pause_menu.handle_click(event.pos)
                if result == "resume":
                    game_state = "playing"
                    pause_menu.active = False
                elif result == "quit":
                    running = False

            elif game_state == "start":
                result = start_menu.handle_click(event.pos)
                if result == "start":
                    score_display.reset()
                    current_floor = 1
                    (
                        player,
                        floor_background,
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
                    if shoot_sound is not None:
                        player.shoot_sound = shoot_sound
                    merchant = spawn_merchant(room_manager)
                    game_state = "playing"
                elif result == "quit":
                    running = False

            elif game_state == "finished":
                result = finish_menu.handle_click(event.pos)
                if result == "quit":
                    running = False
                    
            elif game_state == "dead":
                result = death_menu.handle_click(event.pos)
                if result == "restart":
                    current_floor = 1
                    score_display.reset()  
                    (
                        player,
                        floor_background,
                        walls_group,
                        enemies,
                        player_bullets,
                        enemy_bullets,
                        doors_group,
                        room_manager,
                        exit_group,
                        loot_manager,
                    ) = init_game()
                    pygame.mixer.music.play(-1)
                    if hasattr(player, "gold"):
                        player.gold = 0
                    if shoot_sound is not None:
                        player.shoot_sound = shoot_sound

                    merchant = spawn_merchant(room_manager)
                    game_state = "playing"
                    death_menu.active = False
                    
                elif result == "quit":
                    running = False

    if game_state == "playing":
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

        # Передаем пустую группу вместо удаленной all_sprites, чтобы не ломать room_manager
        room_manager.update(
            player, enemies, pygame.sprite.Group(), walls_group, doors_group, loot_manager
        )

        if room_manager.room_just_cleared:
            score_display.add_room_clear_points()

        if room_manager.card_event_pending:
            drawn_cards = card_deck.draw(3)
            card_ui.set_cards(drawn_cards)
            game_state = "card_select"
            room_manager.card_event_pending = False

        loot_manager.update_magnet(player)

        collected_coins = loot_manager.update(player)
        if hasattr(player, "gold"):
            player.gold += collected_coins
            if collected_coins > 0:
                score_display.add_coin_points(collected_coins)

        loot_manager.collect_exp(player, room_manager)

        hits = pygame.sprite.groupcollide(player_bullets, enemies, True, False)
        for bullet, hit_list in hits.items():
            for e in hit_list:
                died = e.take_damage(bullet.damage)

        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for b in hits:
            died = player.take_damage(b.damage)
            if died:
                final_score_saved = score_manager.score
                score_manager.add_to_top(final_score_saved)

                pygame.mixer.music.stop()
                pygame.mixer.music.rewind()

                death_sound.play()
                pygame.event.pump()

                game_state = "dead"
                death_menu.active = True

        if player.is_dead and pygame.time.get_ticks() - player.death_time > 1333:
            final_score_saved = score_manager.score
            score_manager.add_to_top(final_score_saved)

            pygame.mixer.music.stop()
            pygame.mixer.music.rewind()

            death_sound.play()
            pygame.event.pump()

            game_state = "dead"
            death_menu.active = True

        all_combat_cleared = (
            all(room.cleared for room in room_manager.combat_rooms)
            if room_manager.combat_rooms
            else True
        )
        
        if all_combat_cleared and pygame.sprite.spritecollide(
                player, exit_group, False
        ):
            if current_floor >= settings.MAX_FLOORS:
                final_score_saved = score_manager.score
                score_manager.add_to_top(final_score_saved)
                game_state = "finished"
            else:
                current_floor += 1
                (
                    player,
                    floor_background,
                    walls_group,
                    enemies,
                    player_bullets,
                    enemy_bullets,
                    doors_group,
                    room_manager,
                    exit_group,
                    loot_manager,
                ) = init_game(existing_player=player)
                if shoot_sound is not None:
                    player.shoot_sound = shoot_sound
                merchant = spawn_merchant(room_manager)

    # --- РЕНДЕРИНГ И ЭКРАНЫ ---
    if game_state == "start":
        start_menu.draw(screen)
        pygame.display.flip()
        continue

    if game_state == "finished":
        finish_menu.draw(screen, final_score=final_score_saved)
        pygame.display.flip()
        continue

    # 1. Очистка экрана
    screen.fill((20, 20, 20)) 

    # 2. Рендеринг пола (Один большой запеченный холст сдвигается камерой)
    floor_rect = floor_background.get_rect()
    screen.blit(floor_background, camera.apply(floor_rect))

    # 3. Объекты уровня поверх пола
    for wall in walls_group:
        screen.blit(wall.image, camera.apply(wall.rect))
    for ev in exit_group:
        screen.blit(ev.image, camera.apply(ev.rect))

    loot_manager.draw(screen, camera)

    # 4. Существа и снаряды
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

    # 5. UI меню и HUD поверх игрового мира
    hud.draw(screen, player, current_floor, score_manager=score_manager, run_timer=run_timer)

    if game_state == "card_select":
        card_ui.draw(screen)

    if game_state == "paused":
        pause_menu.draw(screen)
        
    if game_state == "dead":
        death_menu.draw(screen, final_score=final_score_saved, score_manager=score_manager)

    pygame.display.flip()

pygame.quit()
sys.exit()