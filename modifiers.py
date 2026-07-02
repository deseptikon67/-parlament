class BuffManager:
    def __init__(self):
        self.active: dict[str, float] = {}

    def apply_card(self, card):
        self.active[card.buff_stat] = card.buff_value
        self.active[card.debuff_stat] = card.debuff_value

    def clear(self):
        self.active = {}

    def get_multiplier(self, stat_name: str) -> float:
        return self.active.get(stat_name, 1.0)
