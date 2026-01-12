import json
from datetime import date, timedelta
from pathlib import Path

DATA_FILE = Path("habits.json")


def today():
    return date.today()


def parse_date(d: str) -> date:
    return date.fromisoformat(d)


def date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


class HabitStore:
    def __init__(self):
        self.data = {"habits": {}}
        self.load()

    def load(self):
        if DATA_FILE.exists():
            self.data = json.loads(DATA_FILE.read_text())

    def save(self):
        DATA_FILE.write_text(json.dumps(self.data, indent=2))

    # ---------- Habit Management ----------

    def create_habit(self, name, category=None):
        if not name or name in self.data["habits"]:
            raise ValueError("Invalid or duplicate habit name")

        self.data["habits"][name] = {
            "name": name,
            "start_date": today().isoformat(),
            "category": category,
            "archived": False,
            "history": {}
        }
        self.save()

    def delete_habit(self, name):
        del self.data["habits"][name]
        self.save()

    # ---------- Daily Check-In ----------

    def set_today(self, habit_name, completed: bool):
        habit = self.data["habits"][habit_name]
        habit["history"][today().isoformat()] = completed
        self.save()

    # ---------- Streak Calculations ----------

    def current_streak(self, habit_name) -> int:
        habit = self.data["habits"][habit_name]
        history = habit["history"]

        streak = 0
        d = today()

        while True:
            key = d.isoformat()
            if history.get(key) is True:
                streak += 1
                d -= timedelta(days=1)
            else:
                break

        return streak

    def longest_streak(self, habit_name) -> int:
        habit = self.data["habits"][habit_name]
        history = habit["history"]

        longest = 0
        current = 0

        sorted_days = sorted(parse_date(d) for d in history)

        for d in sorted_days:
            if history[d.isoformat()]:
                current += 1
                longest = max(longest, current)
            else:
                current = 0

        return longest

    def completion_rate(self, habit_name) -> float:
        habit = self.data["habits"][habit_name]
        start = parse_date(habit["start_date"])
        end = today()

        total_days = (end - start).days + 1
        completed = sum(
            1 for d in date_range(start, end)
            if habit["history"].get(d.isoformat()) is True
        )

        return completed / total_days if total_days else 0.0
