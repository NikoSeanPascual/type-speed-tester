import customtkinter as ctk
import git
from datetime import datetime, timedelta
import os


class GitVisualizer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Niko's Local Git Pulse")
        self.geometry("1100x600")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkScrollableFrame(self, width=250, label_text="Local Repositories")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.main_view = ctk.CTkFrame(self)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.repo_title = ctk.CTkLabel(self.main_view, text="Select a Repository", font=("Inter", 24, "bold"))
        self.repo_title.pack(pady=20)

        self.canvas = ctk.CTkCanvas(self.main_view, height=150, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill="x", padx=40, pady=10)

        self.log_frame = ctk.CTkScrollableFrame(self.main_view, label_text="Recent Activity")
        self.log_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_repositories()

    def load_repositories(self):
        base_path = r"/documents"  # Change this to your projects folder

        if not os.path.exists(base_path):
            print(f"Warning: The path {base_path} does not exist!")
            return

        print(f"Scanning: {base_path}")

        try:
            for folder in os.listdir(base_path):
                full_path = os.path.join(base_path, folder)
                if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, ".git")):
                    print(f"Found Repo: {folder}")
                    btn = ctk.CTkButton(self.sidebar, text=f"📦 {folder}",
                                        fg_color="transparent", anchor="w",
                                        command=lambda p=full_path, n=folder: self.show_repo_data(p, n))
                    btn.pack(fill="x", pady=2)
        except Exception as e:
            print(f"Error loading repos: {e}")


    def show_repo_data(self, path, name):
        self.repo_title.configure(text=name)
        for widget in self.log_frame.winfo_children():
            widget.destroy()

        repo = git.Repo(path)
        commits = list(repo.iter_commits('HEAD', max_count=100))

        activity_map = {}
        for commit in repo.iter_commits('HEAD'):
            date = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d')
            activity_map[date] = activity_map.get(date, 0) + 1

        self.draw_heatmap(activity_map)
        self.populate_log(commits)

    def get_color(self, count):
        if count == 0:
            return "#393939"  # Empty (Dark Gray)
        elif count < 3:
            return "#0e4429"  # Low activity (Dark Green)
        elif count < 6:
            return "#006d32"  # Medium activity (Medium Green)
        else:
            return "#39d353"  # High activity (Bright Green)

    def draw_heatmap(self, data):
        self.canvas.delete("all")
        square_size = 12
        gap = 3

        for week in range(52):
            for day in range(7):
                target_date = (datetime.now() - timedelta(days=(51 - week) * 7 + (6 - day))).strftime('%Y-%m-%d')
                count = data.get(target_date, 0)
                color = self.get_color(count)

                x0 = week * (square_size + gap)
                y0 = day * (square_size + gap)
                self.canvas.create_rectangle(x0, y0, x0 + square_size, y0 + square_size, fill=color, outline="")
    def populate_log(self, commits):
        for c in commits:
            msg = c.summary[:50] + "..." if len(c.summary) > 50 else c.summary
            date = datetime.fromtimestamp(c.committed_date).strftime('%Y-%m-%d %H:%M')

            lbl = ctk.CTkLabel(self.log_frame, text=f" {date} │ {c.hexsha[:7]} │ {msg}",
                               anchor="w", font=("Consolas", 12))
            lbl.pack(fill="x", pady=1)


if __name__ == "__main__":
    app = GitVisualizer()
    app.mainloop()