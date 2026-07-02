import json
import os

SAVE_FILE = "best_runs.json"


class ScoreManager:
    def __init__(self):
        self.score = 0

    # --- начисление ---
    def kill(self):
        self.score += 10

    def room_clear(self):
        self.score += 50

    def coin(self):
        self.score += 1

    def reset(self):
        self.score = 0

    # --- сохранить забег ---
    def save_run(self):
        runs = self.load_runs()

        runs.append(self.score)

        # сортировка и топ 3
        runs = sorted(runs, reverse=True)[:3]

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(runs, f)

    # --- загрузка ---
    def load_runs(self):
        if not os.path.exists(SAVE_FILE):
            return []

        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                # защита если файл сломан
                if not isinstance(data, list):
                    return []

                return data

        except:
            return []

    def get_top3(self):
        return self.load_runs()