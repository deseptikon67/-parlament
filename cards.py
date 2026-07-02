import random
from dataclasses import dataclass

STAT_LABELS = {
    "damage_dealt": "урон",
    "damage_taken": "уязвимость",
    "move_speed": "скорость",
    "shoot_cooldown": "скорострельность",
}

# stat_name, для которых выводимое слово описывает обратную величину
# (shoot_cooldown — длительность кулдауна, а "скорострельность" — частота выстрелов)
INVERTED_STATS = {"shoot_cooldown"}


def format_stat(stat_name: str, value: float) -> str:
    """value — множитель (1.7 = +70%, 0.75 = -25%)."""
    display_value = (1 / value) if stat_name in INVERTED_STATS else value
    percent = round((display_value - 1) * 100)
    sign = "+" if percent >= 0 else "-"
    label = STAT_LABELS.get(stat_name, stat_name)
    return f"{sign}{abs(percent)}% {label}"


@dataclass(frozen=True)
class Card:
    id: str
    name: str
    suit: str
    buff_stat: str
    buff_value: float
    debuff_stat: str
    debuff_value: float

    @property
    def buff_text(self) -> str:
        return format_stat(self.buff_stat, self.buff_value)

    @property
    def debuff_text(self) -> str:
        return format_stat(self.debuff_stat, self.debuff_value)


ALL_CARDS: list[Card] = [
    Card("ace_spades", "Туз пик", "♠", "damage_dealt", 1.7, "damage_taken", 1.8),
    Card("king_hearts", "Король червей", "♥", "move_speed", 1.5, "damage_taken", 1.6),
    Card("queen_diamonds", "Дама бубен", "♦", "damage_dealt", 1.5, "shoot_cooldown", 1.7),
    Card("jack_clubs", "Валет треф", "♣", "move_speed", 1.4, "damage_dealt", 0.75),
    Card("va_bank", "Ва-банк", "♠", "damage_dealt", 2.0, "damage_taken", 2.0),
    Card("double_stake", "Двойная ставка", "♥", "damage_dealt", 1.4, "move_speed", 0.7),
    Card("bluff", "Блеф", "♦", "shoot_cooldown", 0.6, "damage_taken", 1.5),
    Card("all_in", "Олл-ин", "♣", "damage_dealt", 1.8, "shoot_cooldown", 1.5),
    Card("lucky_seven", "Счастливая семёрка", "♦", "move_speed", 1.6, "damage_dealt", 0.8),
    Card("house_edge", "Преимущество казино", "♠", "damage_taken", 0.7, "damage_dealt", 0.8),
    Card("hot_streak", "Удачная серия", "♥", "shoot_cooldown", 0.5, "damage_taken", 1.4),
    Card("cold_read", "Холодный расчёт", "♣", "damage_taken", 0.6, "move_speed", 0.75),
]

_CARDS_BY_ID = {c.id: c for c in ALL_CARDS}


class CardDeck:
    def __init__(self):
        self._all_ids = [c.id for c in ALL_CARDS]
        self.pool: list[str] = []
        self._reshuffle()

    def _reshuffle(self):
        self.pool = self._all_ids.copy()
        random.shuffle(self.pool)

    def draw(self, n: int = 4) -> list[Card]:
        if len(self.pool) < n:
            self._reshuffle()
        drawn_ids = self.pool[:n]
        return [_CARDS_BY_ID[cid] for cid in drawn_ids]

    def mark_chosen(self, card_id: str):
        if card_id in self.pool:
            self.pool.remove(card_id)
        if not self.pool:
            self._reshuffle()

    def reset(self):
        self._reshuffle()