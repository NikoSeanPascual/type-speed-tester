import customtkinter as ctk
import pygetwindow as gw
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = "usage_stats.json"
CONFIG_FILE = "app_config.json"


class TrackerEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = self.load_data()
        self.categories = self.load_categories()
        self.current_app = "None"
        self.last_active_time = time.time()
        self.idle_threshold = 120
        self.running = True

    @staticmethod
    def load_data():
        if Path(DATA_FILE).exists():
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def load_categories():
        if Path(CONFIG_FILE).exists():
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"PyCharm": "Coding", "Chrome": "Browsing", "Code": "Coding"}

    def save_all(self):
        with self.lock:
            with open(DATA_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.categories, f, indent=4)

    @staticmethod
    def get_date_str(days_ago=0):
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")

    def update_usage(self):
        while self.running:
            try:
                window = gw.getActiveWindow()
                if window and window.title:
                    parts = window.title.split("-")
                    app_name = parts[-1].strip() if parts else "Unknown"

                    today = self.get_date_str()

                    with self.lock:
                        if today not in self.data:
                            self.data[today] = {}

                        if app_name != self.current_app:
                            self.last_active_time = time.time()
                            self.current_app = app_name

                        if time.time() - self.last_active_time < self.idle_threshold:
                            self.data[today][app_name] = self.data[today].get(app_name, 0) + 1
            except (AttributeError, IndexError):
                pass

            time.sleep(1)
            if int(time.time()) % 30 == 0:
                self.save_all()


class AppDashboard(ctk.CTk):
    def __init__(self, tracker_engine):
        super().__init__()
        self.engine = tracker_engine
        self.current_view = "live"
        self.sidebar = None
        self.btn_live = None
        self.btn_hist = None
        self.main_container = None
        self.header_label = None
        self.scroll_frame = None

        self.title("NikoFlow | App Usage Tracker")
        self.geometry("1000x650")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_view()

        threading.Thread(target=self.engine.update_usage, daemon=True).start()
        self.refresh_loop()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="NikoFlow", font=("Fixedsys", 32, "bold"), text_color="#2ecc71").pack(pady=20)

        self.btn_live = ctk.CTkButton(self.sidebar,
                                      font=("Fixedsys", 10, "bold"),
                                      text="Live Dashboard",
                                      fg_color="#2ecc71",
                                      hover_color="#1A491D",
                                      command=lambda: self.show_view("live"))
        self.btn_live.pack(pady=10, padx=20)

        self.btn_hist = ctk.CTkButton(self.sidebar,
                                      font=("Fixedsys", 9, "bold"),
                                      text="History Breakdown",
                                      fg_color="transparent",
                                      hover_color="#B6B0B0",
                                      border_width=1,
                                      command=lambda: self.show_view("history"))
        self.btn_hist.pack(pady=10, padx=20)

    def setup_main_view(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.header_label = ctk.CTkLabel(self.main_container, text="Real-time Activity", font=("Fixedsys", 24, "bold"), text_color="#2ecc71")
        self.header_label.pack(anchor="w", pady=(0, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="#1a1a1a")
        self.scroll_frame.pack(fill="both", expand=True)

    def show_view(self, view_name):
        self.current_view = view_name
        if view_name == "live":
            self.header_label.configure(text="Real-time Activity")
            self.btn_live.configure(fg_color="#2ecc71")
            self.btn_hist.configure(fg_color="transparent")
        else:
            self.header_label.configure(text="History: Last 7 Days")
            self.btn_hist.configure(fg_color="#2ecc71")
            self.btn_live.configure(fg_color="transparent")
        self.refresh_ui()

    @staticmethod
    def format_time(seconds):
        h, m = divmod(seconds, 3600)
        m, s = divmod(m, 60)
        return f"{h}h {m}m {s}s"

    def refresh_ui(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if self.current_view == "live":
            self.render_live_view()
        else:
            self.render_history_view()

    def render_live_view(self):
        today_data = self.engine.data.get(self.engine.get_date_str(), {})
        sorted_apps = sorted(today_data.items(), key=lambda x: x[1], reverse=True)

        active_card = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b")
        active_card.pack(fill="x", pady=(0, 15), padx=5)
        ctk.CTkLabel(active_card, text=f"Currently Using: {self.engine.current_app}",
                     font=("Fixedsys", 14, "bold")).pack(pady=10)

        total_sec = sum(today_data.values())
        for app_name, sec in sorted_apps:
            self.create_app_row(app_name, sec, total_sec)

    def render_history_view(self):
        for i in range(1, 8):
            date_str = self.engine.get_date_str(days_ago=i)
            day_total = sum(self.engine.data.get(date_str, {}).values())

            day_frame = ctk.CTkFrame(self.scroll_frame)
            day_frame.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(day_frame, text=date_str, font=("Segoi UI", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(day_frame, text=f"Total: {self.format_time(day_total)}").pack(side="right", padx=10)

    def create_app_row(self, app_name, sec, total):
        row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row.pack(fill="x", pady=5)

        category = self.engine.categories.get(app_name, "Uncategorized")
        ctk.CTkLabel(row, text=app_name, width=150, anchor="w").pack(side="left", padx=5)

        badge_color = "#4a4a4a" if category == "Uncategorized" else "#2e7d32"
        ctk.CTkLabel(row, text=category, font=("Fixedsys", 10), fg_color=badge_color, corner_radius=6).pack(side="left",
                                                                                                            padx=5)

        progress = sec / total if total > 0 else 0
        pb = ctk.CTkProgressBar(row, width=250)
        pb.set(progress)
        pb.pack(side="left", padx=20)

        ctk.CTkLabel(row, text=self.format_time(sec), font=("Fixedsys", 12)).pack(side="right", padx=5)

    def refresh_loop(self):
        if self.current_view == "live":
            self.refresh_ui()
        self.after(2000, self.refresh_loop)



if __name__ == "__main__":
    main_engine = TrackerEngine()
    main_app = AppDashboard(main_engine)
    main_app.mainloop()