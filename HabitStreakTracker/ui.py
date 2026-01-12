import customtkinter as ctk
from datetime import date, timedelta
from data import HabitStore

# ---------------- Theme ----------------

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

BG_COLOR = "#050805"
FG_COLOR = "#00ff66"
DIM_COLOR = "#003b1f"
ACCENT = "#00ff88"


class HabitApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- Core ----------------
        self.store = HabitStore()
        self.selected_habit = None

        self.title("HABIT_STREAK.EXE")
        self.geometry("1000x550")
        self.configure(fg_color=BG_COLOR)

        # ---------------- Fonts (AFTER ROOT) ----------------
        try:
            self.font = ctk.CTkFont(family="FixedSys", size=14)
            self.font_big = ctk.CTkFont(family="FixedSys", size=20)
        except Exception:
            self.font = ctk.CTkFont(family="Courier New", size=14)
            self.font_big = ctk.CTkFont(family="Courier New", size=20)

        # ---------------- UI ----------------
        self._build_layout()
        self.refresh_habit_list()

    # ---------------- Layout ----------------

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------- Left Panel ----------
        self.left = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.left.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        self.left_label = ctk.CTkLabel(
            self.left, text="HABITS",
            text_color=FG_COLOR, font=self.font
        )
        self.left_label.pack(pady=5)

        self.habit_list = ctk.CTkScrollableFrame(
            self.left, width=240, fg_color=BG_COLOR
        )
        self.habit_list.pack(fill="y", expand=True)

        self.add_entry = ctk.CTkEntry(
            self.left,
            placeholder_text="new_habit",
            fg_color=BG_COLOR,
            text_color=FG_COLOR,
            font=self.font
        )
        self.add_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(
            self.left,
            text="[ ADD ]",
            command=self.add_habit,
            fg_color=DIM_COLOR,
            hover_color=ACCENT,
            text_color=FG_COLOR,
            font=self.font
        )
        self.add_button.pack(pady=5)

        # ---------- Right Panel ----------
        self.right = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            self.right,
            text="NO HABIT SELECTED",
            text_color=ACCENT,
            font=self.font_big
        )
        self.title_label.pack(pady=10)

        self.stats = ctk.CTkLabel(
            self.right,
            text="",
            text_color=FG_COLOR,
            font=self.font,
            justify="left"
        )
        self.stats.pack(pady=10)

        self.warning = ctk.CTkLabel(
            self.right,
            text="",
            text_color="#ff4444",
            font=self.font
        )
        self.warning.pack(pady=5)

        self.check_button = ctk.CTkButton(
            self.right,
            text="[ COMPLETE TODAY ]",
            command=self.toggle_today,
            state="disabled",
            fg_color=DIM_COLOR,
            hover_color=ACCENT,
            text_color=FG_COLOR,
            font=self.font
        )
        self.check_button.pack(pady=10)

        self.heatmap = ctk.CTkFrame(self.right, fg_color=BG_COLOR)
        self.heatmap.pack(pady=15)

    # ---------------- Habit List ----------------

    def refresh_habit_list(self):
        for w in self.habit_list.winfo_children():
            w.destroy()

        for name in self.store.data["habits"]:
            streak = self.store.current_streak(name)

            btn = ctk.CTkButton(
                self.habit_list,
                text=f"{name}  [{streak}]",
                anchor="w",
                command=lambda n=name: self.select_habit(n),
                fg_color=BG_COLOR,
                hover_color=DIM_COLOR,
                text_color=FG_COLOR,
                font=self.font
            )
            btn.pack(fill="x", pady=2)

    def select_habit(self, name):
        self.selected_habit = name
        self.title_label.configure(text=name.upper())
        self.check_button.configure(state="normal")
        self.refresh_details()

    # ---------------- Details ----------------

    def refresh_details(self):
        if not self.selected_habit:
            return

        name = self.selected_habit
        habit = self.store.data["habits"][name]

        current = self.store.current_streak(name)
        longest = self.store.longest_streak(name)
        rate = self.store.completion_rate(name) * 100

        today_key = date.today().isoformat()
        today_done = habit["history"].get(today_key, False)
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        if yesterday in habit["history"] and not habit["history"].get(yesterday):
            self.warning.configure(text="!! STREAK BROKEN YESTERDAY !!")
        else:
            self.warning.configure(text="")

        self.stats.configure(
            text=(
                f"CURRENT STREAK : {current}\n"
                f"LONGEST STREAK : {longest}\n"
                f"COMPLETION     : {rate:.1f}%\n\n"
                f"TODAY STATUS   : {'DONE' if today_done else 'PENDING'}"
            )
        )

        self.check_button.configure(
            text="[ UNCHECK TODAY ]" if today_done else "[ COMPLETE TODAY ]"
        )

        self.draw_heatmap()
        self.refresh_habit_list()

    # ---------------- Actions ----------------

    def toggle_today(self):
        name = self.selected_habit
        today_key = date.today().isoformat()
        habit = self.store.data["habits"][name]

        current = habit["history"].get(today_key, False)
        self.store.set_today(name, not current)
        self.refresh_details()

    def add_habit(self):
        name = self.add_entry.get().strip()
        if not name:
            return
        try:
            self.store.create_habit(name)
            self.add_entry.delete(0, "end")
            self.refresh_habit_list()
        except ValueError:
            pass

    # ---------------- Heatmap ----------------

    def draw_heatmap(self, days=60):
        for w in self.heatmap.winfo_children():
            w.destroy()

        habit = self.store.data["habits"][self.selected_habit]
        start = date.today() - timedelta(days=days - 1)

        row = col = 0
        for i in range(days):
            d = start + timedelta(days=i)
            done = habit["history"].get(d.isoformat())

            color = DIM_COLOR
            if done:
                color = ACCENT
            if d == date.today():
                color = "#44ff44"

            cell = ctk.CTkLabel(
                self.heatmap,
                text=" ",
                width=14,
                height=14,
                fg_color=color
            )
            cell.grid(row=row, column=col, padx=1, pady=1)

            col += 1
            if col == 15:
                col = 0
                row += 1


if __name__ == "__main__":
    HabitApp().mainloop()
