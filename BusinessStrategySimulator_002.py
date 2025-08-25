# Author(s): Dr. Patrick Lemoine
# Business Strategy Simulator

import random
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openpyxl
import json
import numpy as np
import os

class BusinessUnit:
    def __init__(self, name, budget, impact, resilience, agility, talent_level=0.5, special=None):
        self.name = name
        self.budget = budget
        self.impact = impact
        self.resilience = resilience
        self.agility = agility
        self.talent_level = talent_level
        self.special = special or {}

    def effective_impact(self, stress):
        base = self.impact * self.budget * (1 - stress * 0.5)
        talent_bonus = base * (self.talent_level * 0.2)
        special_bonus = base * 0.2 if self.special.get("brand_boost") else 0
        return base + talent_bonus + special_bonus

class EnhancedCompetitorAI:
    def __init__(self, personality, memory_len=5):
        self.personality = personality
        self.memory_len = memory_len
        self.memory = []
        self.last_player_distribution = None

    def observe_outcome(self, player_win, player_dist):
        self.memory.append({'player_win': player_win, 'player_dist': player_dist})
        if len(self.memory) > self.memory_len:
            self.memory.pop(0)
        self.last_player_distribution = player_dist

    def decide_personality(self):
        if len(self.memory) < self.memory_len:
            return
        wins = [m['player_win'] for m in self.memory]
        win_rate = sum(wins) / len(self.memory)
        if win_rate > 0.7:
            self.personality = "aggressive"
        elif win_rate < 0.3:
            self.personality = "defensive"
        else:
            self.personality = "deceptive"

    def adjust_behavior(self, player_strength, competitor_strength, sentiment):
        self.decide_personality()
        return {
            "confidence": self.personality == "aggressive",
            "avoid": self.personality == "defensive",
            "feint": self.personality == "deceptive" or random.random() < 0.1
        }

class Competitor:
    def __init__(self, name, units, personality):
        self.name = name
        self.units = units
        self.ai = EnhancedCompetitorAI(personality)
        self.sentiment = 0.6
        self.stress = 0.3
        self.liquidity = 0.9

    def calculate_total_assets(self):
        return sum(u.budget for u in self.units.values())

class ExternalEvent:
    def __init__(self, name, description, impact_fn):
        self.name = name
        self.description = description
        self.impact_fn = impact_fn

class BusinessCampaignState:
    def __init__(self):
        self.market_types = ["stable", "volatile", "regulated", "expanding", "recessive", "emerging", "saturated", "niche"]
        self.economic_conditions = ["growth", "recession", "inflation", "stagnation", "boom", "crisis"]
        self.quarter_cycle = ["Q1", "Q2", "Q3", "Q4"]

        self.units = self.load_unit_config()

        self.leadership_quality = 0.85
        self.resources = {"cash": 2000, "investment_points": 300, "brand_strength": 0}
        self.sentiment = 0.7
        self.stress = 0.0
        self.liquidity = 1.0
        self.intel_effectiveness = 0.0

        self.current_market = random.choice(self.market_types)
        self.current_economy = random.choice(self.economic_conditions)
        self.current_quarter = random.choice(self.quarter_cycle)

        self.competitors = [
            Competitor("Competitor A", self.load_unit_config(custom=True), "aggressive"),
            Competitor("Competitor B", self.load_unit_config(custom=True), "defensive")
        ]

    def load_unit_config(self, custom=False):
        default_units = {
            "sales_team": BusinessUnit("Sales Team", 3000, 8, 6, 7, talent_level=0.6, special={"brand_boost": True}),
            "marketing": BusinessUnit("Marketing", 1500, 10, 5, 6, talent_level=0.5),
            "rnd": BusinessUnit("R&D", 800, 15, 8, 5, talent_level=0.7, special={"innovation": True}),
            "legal": BusinessUnit("Legal", 400, 4, 13, 3, talent_level=0.4),
            "finance": BusinessUnit("Finance", 1000, 6, 10, 4, talent_level=0.5),
            "analytics": BusinessUnit("Analytics", 300, 5, 7, 4, talent_level=0.5),
            "intelligence": BusinessUnit("Market Intelligence", 100, 2, 2, 7, talent_level=0.6, special={"espionage": 9}),
        }
        if custom:
            config_path = "unit_config.json"
            if os.path.exists(config_path):
                try:
                    with open(config_path) as f:
                        data = json.load(f)
                    units = {}
                    for k, v in data.items():
                        units[k] = BusinessUnit(
                            v.get("name", k),
                            v.get("budget", 1000),
                            v.get("impact", 5),
                            v.get("resilience", 5),
                            v.get("agility", 5),
                            v.get("talent_level", 0.5),
                            v.get("special", {})
                        )
                    return units
                except Exception as e:
                    print(f"Failed loading unit config: {e}")
        return default_units.copy()

    def calculate_total_assets(self, units_dict):
        return sum(u.budget for u in units_dict.values())

    def trigger_external_event(self):
        def tech_breakthrough(state):
            if "rnd" in state.units:
                state.units["rnd"].impact *= 1.3
        def market_crash(state):
            state.liquidity = max(0, state.liquidity - 0.3)
            state.stress = min(1, state.stress + 0.2)
        def regulatory_change(state):
            if "legal" in state.units:
                state.units["legal"].budget += 100

        events = [
            ExternalEvent("Tech Breakthrough", "Innovation gain boosts R&D impact", tech_breakthrough),
            ExternalEvent("Market Crash", "Liquidity drop and increased stress due to crash", market_crash),
            ExternalEvent("Regulatory Change", "Legal costs increase", regulatory_change)
        ]

        event = random.choice(events)
        event.impact_fn(self)
        return event.name, event.description

class BusinessSimulatorGUI:
    LOG_COLORS = {
        'info': 'black', 'success': 'blue', 'failure': 'red', 'investment': 'green',
        'sabotage': 'orange', 'intel': 'purple', 'event': 'brown'
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Business Strategy Simulator with Advanced Features")
        self.fullscreen = False

        self.state = BusinessCampaignState()
        self.player_units = self.state.units.copy()

        self.log_text = ScrolledText(root, state='disabled', width=120, height=22, wrap='word')
        self.log_text.pack(padx=10, pady=5)

        self.fig = Figure(figsize=(12, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Market Share / Sentiment / Stress / Liquidity / Actions / Competitor AI")
        self.ax.set_xlabel("Quarters")
        self.ax.set_ylabel("Values")
        self.ax.set_ylim(0, 1.2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(padx=10, pady=5)

        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="Number of quarters:").grid(row=0, column=0, padx=5)
        self.turns_var = tk.IntVar(value=12)
        self.turns_entry = tk.Entry(control_frame, width=5, textvariable=self.turns_var)
        self.turns_entry.grid(row=0, column=1)

        tk.Label(control_frame, text="Investment % - Sales/Marketing/R&D/Legal/Finance/Analytics/Intel (ex:30/20/15/10/15/5/5):").grid(row=1, column=0, padx=5)
        self.invest_dist_var = tk.StringVar(value="30/20/15/10/15/5/5")
        self.invest_dist_entry = tk.Entry(control_frame, width=25, textvariable=self.invest_dist_var)
        self.invest_dist_entry.grid(row=1, column=1)

        self.run_button = tk.Button(control_frame, text="Start Simulation", command=self.run_simulation)
        self.run_button.grid(row=0, column=2, padx=5)
        self.clear_button = tk.Button(control_frame, text="Reset Logs/Graphs", command=self.clear_logs_graph)
        self.clear_button.grid(row=0, column=3, padx=5)
        self.export_button = tk.Button(control_frame, text="Export Excel Report", command=self.export_excel, state='disabled')
        self.export_button.grid(row=0, column=4, padx=5)

        self.logs = []
        self.sim_data = []

    def log(self, message, event_type="info"):
        self.logs.append(message)
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n", event_type)
        self.log_text.tag_config(event_type, foreground=self.LOG_COLORS.get(event_type,'black'))
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()

    def clear_logs_graph(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
        self.logs.clear()
        self.sim_data.clear()
        self.ax.clear()
        self.ax.set_title("Market Share / Sentiment / Stress / Liquidity / Actions / Competitor AI")
        self.ax.set_xlabel("Quarters")
        self.ax.set_ylabel("Values")
        self.ax.set_ylim(0, 1.2)
        self.canvas.draw()
        self.export_button.config(state='disabled')
        self.log("Logs and graphs cleared.", event_type="event")

    def export_excel(self):
        if not self.sim_data:
            messagebox.showwarning("No data", "No data to export.")
            return
        filename = f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Business Simulation"
        headers = ["Quarter", "Player Market Share", "Competitors Market Share", "Sentiment", "Competitor Sentiment",
                   "Stress", "Liquidity", "Investment Points", "Brand Strength", "Market Type", "Economic Condition",
                   "Actions", "Strategic Actions", "Competitor AI Personality"]
        ws.append(headers)
        for record in self.sim_data:
            ws.append([
                record["quarter"], record["player_market_share"], record["competitor_market_share"],
                round(record["player_sentiment"], 2), round(record["competitor_sentiment"], 2),
                round(record["stress"], 2), round(record["liquidity"], 2),
                record["investment_points"], record["brand_strength"], record["market_type"], record["economic_condition"],
                "; ".join(record["actions"]), record.get("strategic_actions", 0), record.get("competitor_ai", "unknown")
            ])
        wb.save(filename)
        self.log(f"Excel report exported: {filename}", event_type="event")
        messagebox.showinfo("Export done", f"Report saved as:\n{filename}")

    def parse_invest_dist(self, dist):
        try:
            result = [int(x) for x in dist.strip().split('/')]
        except:
            result = [30,20,15,10,15,5,5]
        total = sum(result)
        if total != 100 and total > 0:
            ratio = [x*100//total for x in result]
            return ratio + [0]*(7 - len(ratio))
        return result + [0]*(7 - len(result))

    def run_simulation(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
        self.logs.clear()
        self.sim_data.clear()
        self.export_button.config(state='disabled')
        try:
            turns = int(self.turns_var.get())
            if turns <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Please enter a positive integer for quarters.")
            return
        invest_dist = self.parse_invest_dist(self.invest_dist_var.get())
        self.log(f"=== Starting business simulation with multiple competitors ===", event_type="info")

        player_units = self.player_units
        state = self.state

        for quarter in range(1, turns +1):
            self.log(f"\n--- Quarter {quarter} ---", event_type="info")

            # External event chance
            if random.random() < 0.15:
                event_name, event_desc = state.trigger_external_event()
                self.log(f"External event: {event_name} - {event_desc}", event_type="event")

            # Environment updates
            if quarter % 2 == 0:
                state.current_economy = random.choice(state.economic_conditions)
            state.current_quarter = state.quarter_cycle[(quarter - 1) % 4]
            if random.random() < 0.12:
                state.current_market = random.choice(state.market_types)

            # Player investment
            investment_gain = int(state.resources["investment_points"] * 0.1)
            cash_spent = investment_gain * 5
            if state.resources["cash"] >= cash_spent and investment_gain > 0:
                state.resources["cash"] -= cash_spent
                units_keys = list(player_units.keys())
                for i, key in enumerate(units_keys):
                    add_budget = int(investment_gain * invest_dist[i] / 100)
                    player_units[key].budget += add_budget
                    if add_budget > 0:
                        self.log(f"Invested {add_budget} in {player_units[key].name}.", event_type="investment")
            else:
                self.log("Not enough cash to invest.", event_type="failure")

            # Competitors AI actions
            for comp in state.competitors:
                ai_behavior = comp.ai.adjust_behavior(0,0,comp.sentiment)
                comp_action = "aggressive" if ai_behavior["confidence"] else "defensive" if ai_behavior["avoid"] else "deceptive"
                self.log(f"{comp.name} acts {comp_action}.", event_type="intel")

            # Market competition results
            player_score = sum(u.effective_impact(state.stress) for u in player_units.values())
            competitors_score = sum(comp.calculate_total_assets() for comp in state.competitors)

            if player_score > competitors_score:
                gained = int((player_score - competitors_score) * 0.05)
                lost = int(competitors_score * 0.03)
                for comp in state.competitors:
                    comp_units_loss = lost // len(state.competitors)
                    for u in comp.units.values():
                        u.budget = max(0, u.budget - comp_units_loss)
                for u in player_units.values():
                    u.budget = max(0, u.budget - lost)
                self.log(f"Player gained {gained} market share from competitors.", event_type="success")
            else:
                lost = int((competitors_score - player_score) * 0.06)
                gained = int(player_score * 0.02)
                for u in player_units.values():
                    u.budget = max(0, u.budget - lost)
                for comp in state.competitors:
                    comp_units_gain = gained // len(state.competitors)
                    for u in comp.units.values():
                        u.budget += comp_units_gain
                self.log(f"Player lost {lost} market share.", event_type="failure")

            # Update sentiments, stress, liquidity
            state.sentiment = max(0, min(1, state.sentiment - 0.02 + random.uniform(-0.01,0.02)))
            state.stress = max(0, min(1, state.stress + 0.03 + random.uniform(-0.01,0.01)))
            state.liquidity = max(0, min(1, state.liquidity - 0.01 + random.uniform(-0.01,0.01)))

            # Record turn data
            self.sim_data.append({
                "quarter": quarter,
                "player_market_share": sum(u.budget for u in player_units.values()),
                "competitor_market_share": sum(comp.calculate_total_assets() for comp in state.competitors),
                "player_sentiment": state.sentiment,
                "competitor_sentiment": sum(comp.sentiment for comp in state.competitors) / len(state.competitors),
                "stress": state.stress,
                "liquidity": state.liquidity,
                "investment_points": state.resources["investment_points"],
                "brand_strength": state.resources["brand_strength"],
                "market_type": state.current_market,
                "economic_condition": state.current_economy,
                "actions": [],
                "strategic_actions": 0,
                "competitor_ai": ", ".join([comp.ai.personality for comp in state.competitors])
            })

            self.update_graph()

        # Enable export button after simulation
        self.export_button.config(state='normal')
        self.log("\n=== Simulation Ended ===", event_type="event")

    def update_graph(self):
        if not self.sim_data:
            return
        quarters = [d["quarter"] for d in self.sim_data]
        player_share = [d["player_market_share"]/10000 for d in self.sim_data]
        competitor_share = [d["competitor_market_share"]/10000 for d in self.sim_data]
        sentiment = [d["player_sentiment"] for d in self.sim_data]
        stress = [d["stress"] for d in self.sim_data]
        liquidity = [d["liquidity"] for d in self.sim_data]

        self.ax.clear()
        self.ax.plot(quarters, player_share, label="Player Market Share (norm)", color="blue")
        self.ax.plot(quarters, competitor_share, label="Competitor Market Share (norm)", color="red")
        self.ax.plot(quarters, sentiment, label="Player Sentiment", color="green")
        self.ax.plot(quarters, stress, label="Stress", color="brown")
        self.ax.plot(quarters, liquidity, label="Liquidity", color="orange")

        self.ax.set_title("Market Share / Sentiment / Stress / Liquidity")
        self.ax.set_xlabel("Quarters")
        self.ax.set_ylabel("Value (Normalized)")
        self.ax.legend()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessSimulatorGUI(root)
    root.mainloop()
