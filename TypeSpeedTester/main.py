import customtkinter as ctk
import tkinter as tk
import json
import time
import random

# ================== CONFIG ================== #

APP_WIDTH = 1000
APP_HEIGHT = 600

FONT_MAIN = ("Consolas", 16)
FONT_HEADER = ("Consolas", 24, "bold")

BG_COLOR = "#0b0f0c"
FG_COLOR = "#00ff88"
ERROR_COLOR = "#ff5555"
CURSOR_COLOR = "#00ffaa"

TEST_DURATIONS = [15, 30, 60]
TEXT_FILE = "texts.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def load_text_bank():
    try:
        with open(TEXT_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise SystemExit(f"Failed to load text bank: {e}")


# ================== APP ================== #

class TypingTester(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TERMINAL TYPING TEST")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.configure(fg_color=BG_COLOR)

        self.text_bank = load_text_bank()

        self.target_text = ""
        self.start_time = None
        self.duration = 60
        self.errors = 0
        self.running = False

        self._build_ui()
        self.load_text()

    # ============== UI ============== #

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(
            self,
            text=">> TYPING SPEED TEST",
            font=FONT_HEADER,
            text_color=FG_COLOR
        )
        header.grid(row=0, column=0, columnspan=2, pady=15)

        # Target text display
        self.display = tk.Text(
            self,
            height=6,
            wrap="word",
            font=FONT_MAIN,
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=CURSOR_COLOR,
            bd=0,
            highlightthickness=0
        )
        self.display.grid(row=1, column=0, padx=20, sticky="nsew")
        self.display.config(state="disabled")

        # Input box
        self.input = ctk.CTkTextbox(
            self,
            height=120,
            font=FONT_MAIN,
            fg_color="#050807",
            text_color=FG_COLOR,
            border_color=FG_COLOR
        )
        self.input.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.input.configure(state="disabled")
        self.input.bind("<Key>", self.on_key)

        # Stats panel
        self.stats = ctk.CTkFrame(self, fg_color="#050807")
        self.stats.grid(row=1, column=1, rowspan=2, padx=10, sticky="nsew")

        self.wpm_lbl = self._stat_label("WPM: 0")
        self.acc_lbl = self._stat_label("ACC: 100%")
        self.err_lbl = self._stat_label("ERR: 0")
        self.time_lbl = self._stat_label("TIME: 60s")

        # Controls
        controls = ctk.CTkFrame(self, fg_color=BG_COLOR)
        controls.grid(row=3, column=0, columnspan=2, pady=15)

        ctk.CTkButton(controls, text="START", command=self.start).pack(side="left", padx=10)
        ctk.CTkButton(controls, text="RESET", command=self.reset).pack(side="left", padx=10)

        self.mode_menu = ctk.CTkOptionMenu(
            controls,
            values=list(self.text_bank.keys()),
            command=lambda _: self.load_text()
        )
        self.mode_menu.pack(side="left", padx=10)

        ctk.CTkOptionMenu(
            controls,
            values=[str(t) for t in TEST_DURATIONS],
            command=self.set_time
        ).pack(side="left", padx=10)

        # Text tags
        self.display.tag_config("correct", foreground=FG_COLOR)
        self.display.tag_config("incorrect", foreground=ERROR_COLOR)
        self.display.tag_config("cursor", background="#003322")

    def _stat_label(self, text):
        lbl = ctk.CTkLabel(
            self.stats,
            text=text,
            font=FONT_MAIN,
            text_color=FG_COLOR
        )
        lbl.pack(pady=10)
        return lbl

    # ============== LOGIC ============== #

    def load_text(self):
        mode = self.mode_menu.get()
        self.target_text = random.choice(self.text_bank.get(mode, ["No text available."]))

        self.display.config(state="normal")
        self.display.delete("1.0", "end")
        self.display.insert("1.0", self.target_text)
        self.display.config(state="disabled")

    def set_time(self, value):
        self.duration = int(value)
        self.time_lbl.configure(text=f"TIME: {self.duration}s")

    def start(self):
        self.reset()
        self.input.configure(state="normal")
        self.input.focus()

    def reset(self):
        self.input.configure(state="normal")
        self.input.delete("1.0", "end")
        self.input.configure(state="disabled")

        self.errors = 0
        self.start_time = None
        self.running = False

        self.update_stats(0)
        self.time_lbl.configure(text=f"TIME: {self.duration}s")

    def on_key(self, _):
        typed = self.input.get("1.0", "end-1c")

        if not self.start_time:
            self.start_time = time.time()
            self.running = True
            self.update_timer()

        self.after(1, self.compare)

        if len(typed) >= len(self.target_text):
            self.finish()
            return "break"

    def compare(self):
        typed = self.input.get("1.0", "end-1c")

        self.display.config(state="normal")
        self.display.tag_remove("correct", "1.0", "end")
        self.display.tag_remove("incorrect", "1.0", "end")
        self.display.tag_remove("cursor", "1.0", "end")

        self.errors = 0

        for i, char in enumerate(typed):
            idx = f"1.{i}"
            if char == self.target_text[i]:
                self.display.tag_add("correct", idx)
            else:
                self.display.tag_add("incorrect", idx)
                self.errors += 1

        if len(typed) < len(self.target_text):
            self.display.tag_add("cursor", f"1.{len(typed)}")

        self.display.config(state="disabled")
        self.update_stats(len(typed))

    def update_stats(self, chars):
        elapsed = max(time.time() - self.start_time, 1) if self.start_time else 1
        wpm = int((chars / 5) / (elapsed / 60))
        acc = 100 if chars == 0 else int((chars - self.errors) / chars * 100)

        self.wpm_lbl.configure(text=f"WPM: {wpm}")
        self.acc_lbl.configure(text=f"ACC: {acc}%")
        self.err_lbl.configure(text=f"ERR: {self.errors}")

    def update_timer(self):
        if not self.running:
            return

        remaining = int(self.duration - (time.time() - self.start_time))
        self.time_lbl.configure(text=f"TIME: {remaining}s")

        if remaining <= 0:
            self.finish()
            return

        self.after(100, self.update_timer)

    def finish(self):
        self.running = False
        self.input.configure(state="disabled")
        elapsed = time.time() - self.start_time
        self.time_lbl.configure(text=f"DONE: {elapsed:.1f}s")


# ================== RUN ================== #

if __name__ == "__main__":
    TypingTester().mainloop()
