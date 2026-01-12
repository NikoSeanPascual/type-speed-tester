import customtkinter as ctk
import random

class CityState:
    def __init__(self):
        self.day = 0
        self.running = False
        self.speed = 1

        self.population = 100
        self.food = 500
        self.energy = 300
        self.money = 200

        self.food_prod = 15
        self.energy_prod = 10
        self.money_prod = 8

        self.events = []
        self.log = []
        self.collapsed = False

    def add_log(self, text):
        self.log.append(f"Day {self.day}: {text}")
        if len(self.log) > 100:
            self.log.pop(0)

class SimulationEngine:
    def __init__(self, city: CityState):
        self.city = city

    def tick(self):
        if not self.city.running or self.city.collapsed:
            return

        self.city.day += 1

        self.apply_events()
        self.update_resources()
        self.update_population()
        self.check_status()
        self.random_events()

    def update_resources(self):
        pop = self.city.population

        food_change = self.city.food_prod - pop * 0.5
        energy_change = self.city.energy_prod - pop * 0.3
        money_change = self.city.money_prod - pop * 0.2

        self.city.food = max(0, int(self.city.food + food_change))
        self.city.energy = max(0, int(self.city.energy + energy_change))
        self.city.money = max(0, int(self.city.money + money_change))

    def update_population(self):
        growth_rate = 0.01
        death_rate = 0.005

        if self.city.food < self.city.population:
            death_rate += 0.02

        if self.city.energy < self.city.population * 0.5:
            growth_rate *= 0.3

        net = int(self.city.population * (growth_rate - death_rate))
        self.city.population = max(0, self.city.population + net)

        if net > 0:
            self.city.add_log(f"Population grew by {net}")
        elif net < 0:
            self.city.add_log(f"Population declined by {-net}")

    def random_events(self):
        if random.random() < 0.05:
            event = random.choice([
                ("Drought", 5),
                ("Power Outage", 4),
                ("Economic Boom", 6),
                ("Disease", 5)
            ])
            self.city.events.append({"name": event[0], "days": event[1]})
            self.city.add_log(f"Event started: {event[0]}")

    def apply_events(self):
        for event in self.city.events[:]:
            if event["name"] == "Drought":
                self.city.food_prod = 5
            elif event["name"] == "Power Outage":
                self.city.energy_prod = 3
            elif event["name"] == "Economic Boom":
                self.city.money_prod = 20
            elif event["name"] == "Disease":
                self.city.population = max(0, self.city.population - 3)

            event["days"] -= 1
            if event["days"] <= 0:
                self.city.events.remove(event)
                self.reset_production()
                self.city.add_log(f"Event ended: {event['name']}")

    def reset_production(self):
        self.city.food_prod = 15
        self.city.energy_prod = 10
        self.city.money_prod = 8

    def check_status(self):
        if self.city.population <= 0:
            self.city.collapsed = True
            self.city.running = False
            self.city.add_log("CITY COLLAPSED: No population left")

        if self.city.food == 0:
            self.city.add_log("WARNING: Food shortage")

        if self.city.money == 0:
            self.city.add_log("WARNING: City is bankrupt")


# -----------------------------
# USER INTERFACE
# -----------------------------
class CitySimUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CitySimulation")
        self.geometry("1000x600")

        # ⚠️ IMPORTANT FIX: DO NOT NAME THIS self.state
        self.city = CityState()
        self.engine = SimulationEngine(self.city)

        self.create_layout()
        self.after(1000, self.loop)

    def create_layout(self):
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=5)

        self.day_label = ctk.CTkLabel(top, text="Day: 0")
        self.day_label.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(top, text="PAUSED")
        self.status_label.pack(side="right", padx=10)

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True)

        left = ctk.CTkFrame(main)
        left.pack(side="left", fill="y", padx=5)

        center = ctk.CTkFrame(main)
        center.pack(side="left", fill="both", expand=True, padx=5)

        right = ctk.CTkFrame(main)
        right.pack(side="right", fill="y", padx=5)

        self.pop_label = ctk.CTkLabel(left, text="Population: 0")
        self.pop_label.pack(pady=10)

        self.food_label = ctk.CTkLabel(left, text="Food: 0")
        self.food_label.pack()

        self.energy_label = ctk.CTkLabel(left, text="Energy: 0")
        self.energy_label.pack()

        self.money_label = ctk.CTkLabel(left, text="Money: 0")
        self.money_label.pack()

        self.food_bar = ctk.CTkProgressBar(center)
        self.food_bar.pack(pady=10)

        self.energy_bar = ctk.CTkProgressBar(center)
        self.energy_bar.pack(pady=10)

        self.money_bar = ctk.CTkProgressBar(center)
        self.money_bar.pack(pady=10)

        ctk.CTkButton(right, text="Start / Pause", command=self.toggle).pack(pady=5)
        ctk.CTkButton(right, text="Speed x1", command=lambda: self.set_speed(1)).pack()
        ctk.CTkButton(right, text="Speed x2", command=lambda: self.set_speed(2)).pack()
        ctk.CTkButton(right, text="Speed x5", command=lambda: self.set_speed(5)).pack()

        self.log_box = ctk.CTkTextbox(self, height=120)
        self.log_box.pack(fill="x", padx=10, pady=5)

    def toggle(self):
        if not self.city.collapsed:
            self.city.running = not self.city.running

    def set_speed(self, speed):
        self.city.speed = speed

    def loop(self):
        for _ in range(self.city.speed):
            self.engine.tick()

        self.refresh_ui()
        self.after(1000, self.loop)

    def refresh_ui(self):
        self.day_label.configure(text=f"Day: {self.city.day}")
        self.status_label.configure(
            text="RUNNING" if self.city.running else "PAUSED"
        )

        self.pop_label.configure(text=f"Population: {self.city.population}")
        self.food_label.configure(text=f"Food: {self.city.food}")
        self.energy_label.configure(text=f"Energy: {self.city.energy}")
        self.money_label.configure(text=f"Money: {self.city.money}")

        self.food_bar.set(min(self.city.food / 500, 1))
        self.energy_bar.set(min(self.city.energy / 300, 1))
        self.money_bar.set(min(self.city.money / 300, 1))

        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "\n".join(self.city.log))

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = CitySimUI()
    app.mainloop()
