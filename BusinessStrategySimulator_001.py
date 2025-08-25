# Author(s): Dr. Patrick Lemoine
# Business Strategy Simulator – Sun Tzu Tactics for Modern Competition

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

# Business Unit
class BusinessUnit:
    def __init__(self, name, budget, impact, resilience, agility, special=None):
        self.name = name
        self.budget = budget
        self.impact = impact         # Market influence
        self.resilience = resilience # Protection against competitor attacks
        self.agility = agility       # Speed of action/innovation
        self.special = special or {}

# Competitor AI
class EnhancedCompetitorAI:
    def __init__(self, personality, memory_len=5):
        self.personality = personality    # 'aggressive', 'defensive', 'deceptive'
        self.memory_len = memory_len
        self.memory = []
        self.last_player_distribution = [0.7, 0.15, 0.1, 0.05, 0, 0, 0]  # 7 types

    def observe_outcome(self, player_win, player_dist):
        self.memory.append({'player_win': player_win, 'player_dist': player_dist})
        if len(self.memory) > self.memory_len:
            self.memory.pop(0)
        self.last_player_distribution = player_dist

    def decide_personality(self):
        n = len(self.memory)
        if n < self.memory_len: return
        wins = [m['player_win'] for m in self.memory]
        win_rate = sum(wins) / n
        if win_rate > 0.7:
            self.personality = "aggressive"
        elif win_rate < 0.3:
            self.personality = "defensive"
        else:
            self.personality = "deceptive"

    def suggest_competitor_investment(self):
        p = self.last_player_distribution
        max_index = p.index(max(p))
        weights = list(p)
        if max_index == 0:  # Sales team
            weights = [p[0]*0.7, p[1]+0.1, p[2]+0.2, p[3], p[4], p[5], p[6]]
        elif max_index == 1:  # Marketing
            weights = [p+0.1, p[1]*0.7, p[2], p[3]+0.2, p[4], p[5], p[6]]
        elif max_index == 2:  # R&D
            weights = [p+0.2, p[1], p[2]*0.7, p[3]+0.1, p[4], p[5], p[6]]
        else:
            weights = p
        norm = sum(weights)
        if norm == 0:
            return [0.7, 0.15, 0.1, 0.05, 0, 0, 0]
        return [round(x/norm, 2) for x in weights]

    def adjust_behavior(self, player_strength, competitor_strength, sentiment):
        self.decide_personality()
        return {
            "confidence": self.personality == "aggressive",
            "avoid": self.personality == "defensive",
            "feint": self.personality == "deceptive" or random.random() < 0.1
        }

# Simulation State
class BusinessCampaignState:
    def __init__(self):
        self.init_state()

    def init_state(self, sales_team=3000, marketing=1500, rnd=800, legal=400,
                   finance=1000, analytics=300, intelligence=100,
                   competitor_sales=2800, competitor_marketing=1400, competitor_rnd=700, competitor_legal=350,
                   competitor_finance=900, competitor_analytics=250, competitor_intel=90,
                   leadership=0.85, personality=None):
        self.units = {
            "sales_team": BusinessUnit("Sales Team", sales_team, 8, 6, 7),
            "marketing": BusinessUnit("Marketing", marketing, 10, 5, 6, {"brand_boost": True}),
            "rnd": BusinessUnit("R&D", rnd, 15, 8, 5, {"innovation": True}),
            "legal": BusinessUnit("Legal", legal, 4, 13, 3, {"patent": True}),
            "finance": BusinessUnit("Finance", finance, 6, 10, 4),
            "analytics": BusinessUnit("Analytics", analytics, 5, 7, 4),
            "intelligence": BusinessUnit("Market Intelligence", intelligence, 2, 2, 7, {"espionage": 9}),
        }
        self.competitor_units = {
            "sales_team": BusinessUnit("Competitor Sales Team", competitor_sales, 8, 6, 7),
            "marketing": BusinessUnit("Competitor Marketing", competitor_marketing, 10, 5, 6, {"brand_boost": True}),
            "rnd": BusinessUnit("Competitor R&D", competitor_rnd, 15, 8, 5, {"innovation": True}),
            "legal": BusinessUnit("Competitor Legal", competitor_legal, 4, 13, 3, {"patent": True}),
            "finance": BusinessUnit("Competitor Finance", competitor_finance, 6, 10, 4),
            "analytics": BusinessUnit("Competitor Analytics", competitor_analytics, 5, 7, 4),
            "intelligence": BusinessUnit("Competitor Intelligence", competitor_intel, 2, 2, 7, {"espionage": 8}),
        }
        self.leadership_quality = leadership
        self.resources = {"cash": 2000, "investment_points": 300, "brand_strength": 0}
        self.competitor_ai = EnhancedCompetitorAI(personality or random.choice(["aggressive", "defensive", "deceptive"]))
        self.market_types = ["stable", "volatile", "regulated", "expanding", "recessive", "emerging", "saturated", "niche"]
        self.economic_conditions = ["growth", "recession", "inflation", "stagnation", "boom", "crisis"]
        self.quarter_cycle = ["Q1", "Q2", "Q3", "Q4"]
        self.stress = 0.0
        self.liquidity = 1.0
        self.sentiment = 0.7
        self.competitor_sentiment = 0.6
        self.intel_effectiveness = 0.0
        self.current_market = random.choice(self.market_types)
        self.current_economy = random.choice(self.economic_conditions)
        self.current_quarter = random.choice(self.quarter_cycle)
        self.competitor_total = self.calculate_total_assets(self.competitor_units)

    def calculate_total_assets(self, units_dict):
        return sum(unit.budget for unit in units_dict.values())

# GUI
class BusinessSimulatorGUI:
    LOG_COLORS = {
        'info': 'black', 'success': 'blue', 'failure': 'red', 'investment': 'green',
        'sabotage': 'orange', 'intel': 'purple', 'event': 'brown'
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Business Strategy Simulator – Modern Sun Tzu Tactics")
        self.fullscreen = False

        self.state = BusinessCampaignState()

        self.log_text = ScrolledText(root, state='disabled', width=120, height=22, wrap='word')
        self.log_text.pack(padx=10, pady=5)

        self.fig = Figure(figsize=(12, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Market Share / Sentiment / Stress / Liquidity / Actions / Competitor AI Evolution")
        self.ax.set_xlabel("Quarters")
        self.ax.set_ylabel("Values")
        self.ax.set_ylim(0, 1.2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(padx=10, pady=5)

        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="Number of quarters:").grid(row=0, column=0, padx=5)
        self.turns_var = tk.IntVar(value=8)
        self.turns_entry = tk.Entry(control_frame, width=5, textvariable=self.turns_var)
        self.turns_entry.grid(row=0, column=1)

        tk.Label(control_frame, text="Investment % - Sales/Marketing/R&D/Legal/Finance/Analytics/Intel (ex:30/20/15/10/15/5/5):").grid(row=1, column=0, padx=5)
        self.invest_dist_var = tk.StringVar(value="30/20/15/10/15/5/5")
        self.invest_dist_entry = tk.Entry(control_frame, width=25, textvariable=self.invest_dist_var)
        self.invest_dist_entry.grid(row=1, column=1)

        self.run_button = tk.Button(control_frame, text="Start Simulation", command=self.run_simulation)
        self.run_button.grid(row=0, column=2, padx=5)
        self.clear_button = tk.Button(control_frame, text="Reset", command=self.clear_logs_graph)
        self.clear_button.grid(row=0, column=3, padx=5)
        self.export_button = tk.Button(control_frame, text="Export Excel Report", command=self.export_excel, state='disabled')
        self.export_button.grid(row=0, column=4, padx=5)
        self.save_button = tk.Button(control_frame, text="Save", command=self.save_campaign)
        self.save_button.grid(row=1, column=2, padx=5)
        self.load_button = tk.Button(control_frame, text="Load", command=self.load_campaign)
        self.load_button.grid(row=1, column=3, padx=5)
        self.full_button = tk.Button(control_frame, text="Full screen", command=self.toggle_fullscreen)
        self.full_button.grid(row=1, column=4, padx=5)

        self.logs = []
        self.sim_data = []

        self.init_advanced_parameters()

    def log(self, message, event_type="info"):
        self.logs.append(message)
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n", event_type)
        self.log_text.tag_config(event_type, foreground=self.LOG_COLORS.get(event_type, 'black'))
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
        self.ax.set_title("Market Share / Sentiment / Stress / Liquidity / Actions / Competitor AI Evolution")
        self.ax.set_xlabel("Quarters")
        self.ax.set_ylabel("Values")
        self.ax.set_ylim(0, 1.2)
        self.canvas.draw()
        self.export_button.config(state='disabled')
        self.log("Logs and charts reset.", event_type="event")

    def export_excel(self):
        if not self.sim_data:
            messagebox.showwarning("No data", "No data available to export.")
            return
        filename = f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Business Simulation"
        headers = ["Quarter", "Market Share", "Competitor Share", "Sentiment", "Competitor Sentiment",
                   "Stress", "Liquidity", "Cash", "Investment Points", "Brand Strength", "Market",
                   "Economic Context", "Main Actions", "Strategic Actions", "Competitor AI Strategy"]
        ws.append(headers)
        for record in self.sim_data:
            ws.append([
                record["quarter"], record["market_share"], record["competitor_share"],
                round(record["sentiment"], 2), round(record["competitor_sentiment"], 2),
                round(record["stress"], 2), round(record["liquidity"], 2),
                record["resources"]["cash"], record["resources"]["investment_points"],
                record["resources"]["brand_strength"], record["market"],
                record["economy"],
                "; ".join(record["actions"]),
                record.get("strategic_actions", 0),
                record.get("competitor_ai", "unknown")
            ])
        wb.save(filename)
        self.log(f"Excel report exported: {filename}", event_type="event")
        messagebox.showinfo("Export done", f"Report saved as:\n{filename}")

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)

    def save_campaign(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if file:
            data = {
                "sim_data": self.sim_data,
                "state": {
                    "resources": self.state.resources,
                    "units": {k: v.budget for k, v in self.state.units.items()},
                    "competitor_units": {k: v.budget for k, v in self.state.competitor_units.items()},
                    "sentiment": self.state.sentiment,
                    "competitor_sentiment": self.state.competitor_sentiment,
                    "stress": self.state.stress,
                    "liquidity": self.state.liquidity,
                    "leadership_quality": self.state.leadership_quality,
                    "competitor_ai": self.state.competitor_ai.personality,
                    "current_market": self.state.current_market,
                    "current_economy": self.state.current_economy,
                    "current_quarter": self.state.current_quarter,
                }
            }
            with open(file, "w") as f:
                json.dump(data, f)
            self.log(f"Simulation saved ({file})", event_type="event")

    def load_campaign(self):
        file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if file:
            with open(file, "r") as f:
                data = json.load(f)
            self.sim_data = data["sim_data"]
            loaded = data["state"]
            self.state.resources = loaded["resources"]
            for k, c in loaded["units"].items():
                self.state.units[k].budget = c
            for k, c in loaded["competitor_units"].items():
                self.state.competitor_units[k].budget = c
            self.state.sentiment = loaded["sentiment"]
            self.state.competitor_sentiment = loaded["competitor_sentiment"]
            self.state.stress = loaded["stress"]
            self.state.liquidity = loaded["liquidity"]
            self.state.leadership_quality = loaded["leadership_quality"]
            self.state.competitor_ai.personality = loaded["competitor_ai"]
            self.state.current_market = loaded["current_market"]
            self.state.current_economy = loaded["current_economy"]
            self.state.current_quarter = loaded["current_quarter"]
            self.update_graph()
            self.log("Simulation loaded successfully.", event_type="event")

    def init_advanced_parameters(self):
        self.state.init_state()

    def modern_business_tactics(self, quarter, competitor_sentiment, competitor_assets, player_assets):
        actions = []
        if competitor_sentiment > 0.7 and quarter % 3 == 0:
            actions.append("Aggressive marketing campaign distracts competitors.")
            competitor_sentiment -= 0.1
        if player_assets > competitor_assets * 1.2 and competitor_sentiment < 0.4:
            actions.append("Leave a competitor niche unchallenged to avoid price war.")
            competitor_sentiment += 0.05
        if competitor_assets > player_assets and quarter % 4 == 0:
            actions.append("Disrupt competitor supply chain to weaken distribution.")
            competitor_assets -= int(competitor_assets * 0.05)
        if competitor_assets > player_assets and competitor_sentiment > 0.5 and quarter % 5 == 0:
            actions.append("Launch a product earlier to surprise the competitor.")
            if random.random() > 0.5:
                actions.append("Successful launch! Competitor market share decreased.")
                competitor_assets -= int(competitor_assets * 0.1)
            else:
                actions.append("Failed launch, internal confusion.")
        return actions, max(0, min(competitor_sentiment, 1)), max(0, competitor_assets)

    def resolve_market_competition(self):
        player_score = 0
        competitor_score = 0
        for u in self.state.units.values():
            score = u.impact * u.budget * (1 - self.state.stress * 0.5)
            if u.special.get("brand_boost"):
                score *= 1.2
            player_score += score
        for cu in self.state.competitor_units.values():
            score = cu.impact * cu.budget * (1 - self.state.stress * 0.5)
            if cu.special.get("brand_boost"):
                score *= 1.2
            competitor_score += score
        # Market effect: regulation or volatility reduces efficiency of innovation/marketing
        if self.state.current_market in ["regulated", "volatile", "saturated"]:
            for typ in ["marketing", "rnd", "analytics"]:
                if typ in self.state.units:
                    player_score -= self.state.units[typ].impact * self.state.units[typ].budget * 0.2
                if typ in self.state.competitor_units:
                    competitor_score -= self.state.competitor_units[typ].impact * self.state.competitor_units[typ].budget * 0.2
        return max(0, int(player_score)), max(0, int(competitor_score))

    def liquidity_event(self):
        event_message = None
        competitor_intel_level = self.state.competitor_units["intelligence"].budget / 2000
        disruption_chance = 0.1 + competitor_intel_level
        if random.random() < disruption_chance and self.state.liquidity < 0.6:
            stress_penalty = random.uniform(0.1, 0.2)
            self.state.stress += stress_penalty
            self.state.stress = min(self.state.stress, 1.0)
            event_message = f"Liquidity issue! Stress increased by {stress_penalty:.2f}."
        return event_message

    def calculate_sentiment(self):
        leadership_bonus = (self.state.leadership_quality - 0.5) * 0.3
        intel_bonus = (self.state.intel_effectiveness - 0.5) * 0.2
        economic_penalty = -0.1 if self.state.current_economy in ["recession", "crisis"] else 0
        sentiment = self.state.sentiment - self.state.stress * 0.5 + (self.state.liquidity - 0.5) * 0.4 + leadership_bonus + intel_bonus + economic_penalty
        return max(0, min(sentiment, 1))

    def competitor_decision(self, player_total, competitor_total, sentiment):
        return self.state.competitor_ai.adjust_behavior(player_total, competitor_total, sentiment)

    def environment_effects(self):
        effects = []
        if self.state.current_quarter == "Q4":
            effects.append("Year-end effect: increased stress and tighter budgets.")
            self.state.stress += 0.05
        if self.state.current_economy == "inflation":
            effects.append("Inflation: profitability of marketing and innovation reduced.")
            if "marketing" in self.state.units:
                self.state.units["marketing"].budget = max(0, self.state.units["marketing"].budget - 10)
            if "marketing" in self.state.competitor_units:
                self.state.competitor_units["marketing"].budget = max(0, self.state.competitor_units["marketing"].budget - 10)
        if self.state.current_economy == "growth":
            effects.append("Growth: liquidity strengthened.")
            self.state.liquidity = min(1.0, self.state.liquidity + 0.1)
        return effects

    def resource_management(self, invest_dist):
        invest_gain = int(self.state.resources["investment_points"] * 0.1)
        cash_spent = int(invest_gain * 5)
        invest_types = ["sales_team", "marketing", "rnd", "legal", "finance", "analytics", "intelligence"]
        if self.state.resources["cash"] >= cash_spent and invest_gain > 0:
            self.state.resources["cash"] -= cash_spent
            for i, typ in enumerate(invest_types):
                ibudget = int(invest_gain * invest_dist[i] / 100)
                self.state.units[typ].budget += ibudget
                if ibudget > 0:
                    self.log(f"Invested {ibudget} in {self.state.units[typ].name}.", event_type="investment")
        else:
            self.log("Not enough cash to invest.", event_type="failure")
        if self.state.resources["brand_strength"] > 0:
            brand_maintenance_cost = 50
            if self.state.resources["cash"] >= brand_maintenance_cost:
                self.state.resources["cash"] -= brand_maintenance_cost
                self.state.stress = max(0, self.state.stress - 0.05)
                self.log("Brand strength maintained, stress reduced.", event_type="event")
            else:
                self.state.stress += 0.05
                self.log("Insufficient brand maintenance, stress increased.", event_type="failure")

    def advanced_intel_operations(self):
        actions = []
        if self.state.units["intelligence"].budget > 0:
            sabotage_chance = 0.2 * (self.state.units["intelligence"].budget / 100)
            if random.random() < sabotage_chance:
                liquidity_damage = random.uniform(0.05, 0.12)
                self.state.liquidity = max(0, self.state.liquidity - liquidity_damage)
                actions.append("Market intelligence successfully sabotaged a competitor’s supply chain.")
                self.state.competitor_sentiment = max(0, self.state.competitor_sentiment - 0.05)
            misinformation_chance = 0.18 * (self.state.units["intelligence"].budget / 100)
            if random.random() < misinformation_chance:
                actions.append("Market intelligence spread misinformation, competitor confused.")
                self.state.competitor_sentiment = max(0, self.state.competitor_sentiment - 0.07)
        else:
            actions.append("No market intelligence resource available.")
        self.state.intel_effectiveness = min(1.0, self.state.units["intelligence"].budget / 150)
        return actions

    def post_competition_effects(self, player_losses, competitor_losses):
        sentiment_change = (competitor_losses - player_losses) / 10000
        self.state.resources["investment_points"] += int(sentiment_change * 40)
        self.state.resources["investment_points"] = max(40, self.state.resources["investment_points"])
        if sentiment_change > 0:
            self.log("Market confidence increased! More investment points.", event_type="success")
        else:
            self.log("Market nervousness, confidence fell.", event_type="failure")
        if self.state.stress > 0.8:
            self.log("High stress: reputation drops, reduced gains.", event_type="failure")
            self.state.resources["cash"] = max(0, self.state.resources["cash"] - 100)

    def update_competitor_ai(self, player_losses, competitor_losses):
        player_win = player_losses < competitor_losses
        invest_dist = [self.state.units[t].budget for t in ["sales_team","marketing","rnd","legal","finance","analytics","intelligence"]]
        total = sum(invest_dist)
        player_dist = [x / total if total > 0 else 0 for x in invest_dist]
        self.state.competitor_ai.observe_outcome(player_win, player_dist)
        self.log(f"Competitor AI switches to {self.state.competitor_ai.personality}.", event_type="intel")

    def calculate_total_assets(self, units_dict):
        return sum(u.budget for u in units_dict.values())

    def apply_losses(self, units, losses):
        total = self.calculate_total_assets(units)
        if total == 0 or losses == 0: return
        loss_ratio = min(1, losses / total)
        for ut in units.values():
            lost = int(ut.budget * loss_ratio)
            ut.budget = max(0, ut.budget - lost)

    def update_graph(self):
        quarters = [d["quarter"] for d in self.sim_data]
        market_player = [d["market_share"] / 15000 for d in self.sim_data]
        market_competitor = [d["competitor_share"] / 15000 for d in self.sim_data]
        sentiment = [d["sentiment"] for d in self.sim_data]
        stress = [d["stress"] for d in self.sim_data]
        liquidity = [d["liquidity"] for d in self.sim_data]
        actions_count = [d.get("strategic_actions", 0) for d in self.sim_data]

        personality_map = {"aggressive":1.0, "deceptive":0.5, "defensive":0.0}
        ai_vals = [personality_map.get(d.get("competitor_ai","deceptive"), 0.5) for d in self.sim_data]

        unit_names = ["sales_team", "marketing", "rnd", "legal", "finance", "analytics", "intelligence"]
        player_compo = []
        for d in self.sim_data:
            total_f = d["market_share"] if d["market_share"] > 0 else 1
            compo = []
            for un in unit_names:
                if hasattr(self.state.units[un], "budget"):
                    val = self.state.units[un].budget / total_f if total_f > 0 else 0
                    compo.append(val)
                else:
                    compo.append(0)
            player_compo.append(compo)
        player_compo = np.array(player_compo).T

        self.ax.clear()

        self.ax.plot(quarters, market_player, label="Your Market Share (Norm.)", color='blue')
        self.ax.plot(quarters, market_competitor, label="Competitor Market Share (Norm.)", color='red')
        self.ax.plot(quarters, sentiment, label='Sentiment', color='darkgreen')
        self.ax.plot(quarters, stress, label='Stress', color='brown')
        self.ax.plot(quarters, liquidity, label='Liquidity', color='orange')
        self.ax.plot(quarters, actions_count, label='Strategic Actions', color='purple')
        self.ax.plot(quarters, ai_vals, 'm--', label="Competitor AI (1=Agg,0.5=Dec,0=Def)")

        bottom = np.zeros(len(quarters))
        colors = ['#559966', '#9763a6', '#e6d44a', '#ffa500', '#4a90e2', '#c04adb', '#555555']
        labels = ['Sales', 'Marketing', 'R&D', 'Legal', 'Finance', 'Analytics', 'Intel']
        for idx, (un, color, label) in enumerate(zip(unit_names, colors, labels)):
            self.ax.fill_between(quarters, bottom, bottom + player_compo[idx], color=color, alpha=0.3, step="pre", label=label)
            bottom += player_compo[idx]

        self.ax.set_title("Market Share / Sentiment / Stress / Liquidity / Actions / Competitor AI Evolution")
        self.ax.set_xlabel("Quarters")
        self.ax.set_ylabel("Normalized Values")
        self.ax.set_ylim(0, 1.2)
        self.ax.legend(loc='upper right')
        self.canvas.draw()

    def run_simulation(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
        self.logs.clear()
        self.sim_data.clear()
        self.export_button.config(state='disabled')
        self.init_advanced_parameters()
        try:
            turns = int(self.turns_var.get())
            if turns <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid number of quarters.")
            return
        invest_dist = self.parse_invest_dist(self.invest_dist_var.get())
        self.log(f"=== Starting business simulation (Competitor AI: {self.state.competitor_ai.personality}) ===", event_type="info")

        for turn in range(1, turns + 1):
            self.log(f"\n--- Quarter {turn} ---", event_type="info")

            self.state.current_economy = random.choice(self.state.economic_conditions) if turn % 2 == 0 else self.state.current_economy
            self.state.current_quarter = self.state.quarter_cycle[(turn-1)%4]
            if random.random() < 0.12:
                self.state.current_market = random.choice(self.state.market_types)

            env_effects = self.environment_effects()
            for e in env_effects:
                self.log(e, event_type="event")

            liquidity_event = self.liquidity_event()
            if liquidity_event:
                self.log(liquidity_event, event_type="sabotage")

            advanced_actions, self.state.competitor_sentiment, new_competitor_assets = self.modern_business_tactics(
                turn, self.state.competitor_sentiment, self.calculate_total_assets(self.state.competitor_units),
                self.calculate_total_assets(self.state.units)
            )
            self.state.competitor_total = new_competitor_assets
            for aa in advanced_actions:
                self.log(aa, event_type="event")

            intel_actions = self.advanced_intel_operations()
            for ia in intel_actions:
                self.log(ia, event_type="intel")

            self.resource_management(invest_dist)

            self.state.sentiment = self.calculate_sentiment()

            player_score, competitor_score = self.resolve_market_competition()

            competitor_behavior = self.competitor_decision(player_score, competitor_score, self.state.competitor_sentiment)
            if competitor_behavior["avoid"]:
                self.log("Competitor avoids direct confrontation on key sector.", event_type="event")
                competitor_score *= 0.8
            if competitor_behavior["feint"]:
                self.log("Competitor launches diversion operations.", event_type="intel")
                player_score *= 0.9

            if player_score > competitor_score:
                competitor_losses = int((player_score - competitor_score) * 0.08)
                player_losses = int(competitor_score * 0.04)
                self.log(f"Your company gained {competitor_losses} market share from competitor.", event_type="success")
                self.log(f"Your company lost {player_losses} market share.", event_type="failure")
            else:
                player_losses = int((competitor_score - player_score) * 0.07)
                competitor_losses = int(player_score * 0.03)
                self.log(f"Your company lost {player_losses} market share.", event_type="failure")
                self.log(f"Competitor lost {competitor_losses} market share.", event_type="success")

            self.apply_losses(self.state.units, player_losses)
            self.apply_losses(self.state.competitor_units, competitor_losses)

            stress_gain = 0.05 + player_losses / 15000
            self.state.stress = min(1, self.state.stress + stress_gain)
            liquidity_consumption = 0.09 + stress_gain * 0.5
            self.state.liquidity = max(0, self.state.liquidity - liquidity_consumption)

            self.post_competition_effects(player_losses, competitor_losses)
            self.update_competitor_ai(player_losses, competitor_losses)

            self.log(f"End of quarter {turn}:", event_type="info")
            self.log(f"  Your budgets: Sales={self.state.units['sales_team'].budget}, Marketing={self.state.units['marketing'].budget}, R&D={self.state.units['rnd'].budget}, Legal={self.state.units['legal'].budget}, Finance={self.state.units['finance'].budget}, Analytics={self.state.units['analytics'].budget}, Intelligence={self.state.units['intelligence'].budget}", event_type="info")
            self.log(f"  Competitor budgets: Sales={self.state.competitor_units['sales_team'].budget}, Marketing={self.state.competitor_units['marketing'].budget}, R&D={self.state.competitor_units['rnd'].budget}, Legal={self.state.competitor_units['legal'].budget}, Finance={self.state.competitor_units['finance'].budget}, Analytics={self.state.competitor_units['analytics'].budget}, Intelligence={self.state.competitor_units['intelligence'].budget}", event_type="info")
            self.log(f"  Sentiment: You={self.state.sentiment:.2f}, Competitor={self.state.competitor_sentiment:.2f}", event_type="info")
            self.log(f"  Stress: {self.state.stress:.2f}, Liquidity: {self.state.liquidity:.2f}", event_type="info")
            self.log(f"  Resources: Cash={self.state.resources['cash']}, Investment Points={self.state.resources['investment_points']}, Brand Strength={self.state.resources['brand_strength']}", event_type="info")
            self.log(f"  Market: {self.state.current_market}, Economy: {self.state.current_economy}, Quarter: {self.state.current_quarter}", event_type="info")

            self.sim_data.append({
                "quarter": turn,
                "market_share": self.calculate_total_assets(self.state.units),
                "competitor_share": self.calculate_total_assets(self.state.competitor_units),
                "sentiment": self.state.sentiment,
                "competitor_sentiment": self.state.competitor_sentiment,
                "stress": self.state.stress,
                "liquidity": self.state.liquidity,
                "resources": self.state.resources.copy(),
                "market": self.state.current_market,
                "economy": self.state.current_economy,
                "actions": advanced_actions + intel_actions,
                "strategic_actions": len(advanced_actions + intel_actions),
                "competitor_ai": self.state.competitor_ai.personality
            })
            self.update_graph()

            if self.calculate_total_assets(self.state.units) == 0:
                self.log("Your company has gone bankrupt! Simulation ended.", event_type="failure")
                break
            if self.calculate_total_assets(self.state.competitor_units) == 0:
                self.log("Competitor has been exceeded! Simulation won!", event_type="success")
                break

        self.log("\n=== Simulation ended ===", event_type="event")
        market_share_left = self.calculate_total_assets(self.state.units)
        competitor_share_left = self.calculate_total_assets(self.state.competitor_units)
        self.log(f"Final market share - You: {market_share_left}, Competitor: {competitor_share_left}", event_type="info")
        if market_share_left > competitor_share_left:
            self.log("Simulation successful! Congratulations!", event_type="success")
        else:
            self.log("Simulation lost or suspended.", event_type="failure")
        self.export_button.config(state='normal')

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

if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessSimulatorGUI(root)
    root.mainloop()
