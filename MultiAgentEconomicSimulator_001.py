# Author(s): Dr. Patrick Lemoine

# This program simulates a multi-agent investment market, where each agent manages a portfolio using Sun Tzu’s strategic principles and chess-inspired AI logic.
# It dynamically integrates evolving socio-economic indicators—such as unemployment, inflation, and consumption—which influence agent decisions and market conditions.
# Actions and macro-economic changes are visualized in real time, and a detailed simulation report can be exported for analysis.

import random
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import json

# ===== Socio-Economic Model =====
class SocioEconomicState:
    def __init__(self):
        self.unemployment_rate = random.uniform(0.03, 0.12)
        self.inflation_rate = random.uniform(0.01, 0.08)
        self.consumption_index = random.uniform(0.7, 1.2)
    def update(self):
        self.unemployment_rate += random.uniform(-0.005, 0.007)
        self.unemployment_rate = min(max(self.unemployment_rate, 0.02), 0.20)
        self.inflation_rate += random.uniform(-0.002, 0.003)
        self.inflation_rate = min(max(self.inflation_rate, 0.005), 0.15)
        self.consumption_index += random.uniform(-0.03, 0.03)
        self.consumption_index = min(max(self.consumption_index, 0.4), 1.6)

class AssetType:
    def __init__(self, name, ticker, quantity, volatility, liquidity):
        self.name = name
        self.ticker = ticker
        self.quantity = quantity
        self.volatility = volatility
        self.liquidity = liquidity
    @property
    def price(self):
        simulated_prices = {
            'AAPL': random.uniform(140, 170),
            'GOOG': random.uniform(2500, 3000),
            'TSLA': random.uniform(700, 900),
            'MSFT': random.uniform(280, 350),
            'SPY': random.uniform(400, 450)
        }
        return simulated_prices.get(self.ticker, random.uniform(100, 1000))
    @property
    def value(self):
        return self.quantity * self.price

class SunTzuChessMarketAI:
    def __init__(self, personality, memory_len=7):
        self.personality = personality
        self.memory_len = memory_len
        self.memory = []
        self.phase = "opening"
        self.tension_profile = []
        self.turn_count = 0
    def observe_outcome(self, beat_market, risk_tension):
        self.memory.append({'beat_market': beat_market, 'risk_tension': risk_tension})
        if len(self.memory) > self.memory_len:
            self.memory.pop(0)
        self.tension_profile.append(risk_tension)
        self.turn_count += 1
        self.update_phase()
    def decide_personality(self):
        n = len(self.memory)
        if n < self.memory_len:
            return
        wins = [m['beat_market'] for m in self.memory]
        win_rate = sum(wins) / n
        if win_rate > 0.7:
            self.personality = "bullish"
        elif win_rate < 0.3:
            self.personality = "bearish"
        else:
            self.personality = "sideways"
    def update_phase(self):
        if self.turn_count < 3:
            self.phase = "opening"
        elif max(self.tension_profile[-3:]) > 0.65:
            self.phase = "middlegame"
        elif min(self.tension_profile[-3:]) < 0.35:
            self.phase = "endgame"
        else:
            self.phase = "stability"
    def compute_risk_tension(self, socio, volatility, liquidity):
        return 0.25 * socio.unemployment_rate + 0.25 * socio.inflation_rate + 0.3 * volatility + 0.2 * (1 - liquidity)
    def strategy_recommendations(self, asset, risk_tension, cash, control_central, turn_index):
        recs = []
        if risk_tension > 0.7 and asset.liquidity < 0.5:
            recs.append(f"[DEFENSE] Reduce {asset.ticker}: high tension, low liquidity")
        elif control_central > 0.55 and cash > asset.price:
            recs.append(f"[ATTACK] Strengthen {asset.ticker}: strong central control")
        elif risk_tension < 0.4:
            recs.append(f"[ENDGAME] Stabilize {asset.ticker}: low tension")
        elif asset.volatility > 0.6 and asset.quantity > 0:
            recs.append(f"[FLEXIBILITY] Sell part of {asset.ticker}: volatility high")
        if self.phase == "opening":
            recs.append(f"[PREPARATION] Position {asset.ticker} for next cycle")
        elif self.phase == "middlegame":
            recs.append(f"[TENSION] Exploit imbalances, use mobility")
        elif self.phase == "endgame":
            recs.append(f"[SIMPLIFICATION] Reduce risks, liquidate")
        elif self.phase == "stability":
            recs.append(f"[STABLE] Maximize returns")
        if turn_index % 4 == 0:
            recs.append(f"[ANTICIPATION] Re-evaluate {asset.ticker}: (turn {turn_index})")
        return recs

class MultiAgentInvestor:
    def __init__(self, name, risk_aversion, cash):
        self.name = name
        self.risk_aversion = risk_aversion
        self.cash = cash
        self.assets = {}
        self.personality = random.choice(["bullish", "bearish", "sideways"])
        self.market_ai = SunTzuChessMarketAI(self.personality)
    def evaluate_center_control(self):
        center_tickers = ["AAPL", "GOOG", "MSFT"]
        central_value = sum(asset.value for tk, asset in self.assets.items() if tk in center_tickers)
        total = sum(asset.value for asset in self.assets.values())
        return central_value / total if total > 0 else 0
    def take_turn(self, socio, market_cond, turn_index):
        logs = []
        actions = []
        for ticker, asset in self.assets.items():
            control_central = self.evaluate_center_control()
            risk_tension = self.market_ai.compute_risk_tension(socio, market_cond['volatility'], market_cond['liquidity'])
            recs = self.market_ai.strategy_recommendations(asset, risk_tension, self.cash, control_central, turn_index)
            for r in recs:
                logs.append(f"{self.name} AI: {r}")
            action = {
                "agent": self.name,
                "asset": ticker,
                "personality": self.personality,
                "phase": self.market_ai.phase,
                "decision": None,
                "recommendations": recs,
                "quantity_before": asset.quantity,
                "cash_before": self.cash
            }
            if (self.personality == "bullish" and risk_tension < 0.5 and self.cash > asset.price):
                buy_qty = random.randint(1, 2)
                asset.quantity += buy_qty
                self.cash -= asset.price * buy_qty
                logs.append(f"{self.name}: Bought {buy_qty} {asset.ticker}")
                action["decision"] = f"buy {buy_qty}"
            elif (self.personality == "bearish" and risk_tension > 0.6 and asset.quantity > 1):
                sell_qty = random.randint(1, 2)
                asset.quantity -= sell_qty
                self.cash += asset.price * sell_qty
                logs.append(f"{self.name}: Sold {sell_qty} {asset.ticker}")
                action["decision"] = f"sell {sell_qty}"
            else:
                action["decision"] = "hold"
            action["quantity_after"] = asset.quantity
            action["cash_after"] = self.cash
            actions.append(action)
            beat_market = random.random() > 0.5
            self.market_ai.observe_outcome(beat_market, risk_tension)
            self.market_ai.decide_personality()
        return logs, actions

class MultiAgentPortfolio:
    def __init__(self, n_agents=4):
        self.socio_state = SocioEconomicState()
        self.market_cond = {
            "fear_index": random.uniform(0.1, 0.9),
            "liquidity": random.uniform(0.5, 1.0),
            "volatility": random.uniform(0.14, 0.4)
        }
        self.agents = []
        for i in range(n_agents):
            risk_av = random.uniform(0.1, 0.9)
            agent = MultiAgentInvestor(f"Investor_{i+1}", risk_av, 10000)
            agent.assets = {
                'AAPL': AssetType('Apple', 'AAPL', random.randint(10, 30), 0.2, 0.9),
                'GOOG': AssetType('Google', 'GOOG', random.randint(1, 6), 0.25, 0.85),
                'TSLA': AssetType('Tesla', 'TSLA', random.randint(4, 12), 0.3, 0.8),
                'MSFT': AssetType('Microsoft', 'MSFT', random.randint(5, 15), 0.2, 0.85),
                'SPY': AssetType('S&P 500 ETF', 'SPY', random.randint(4, 20), 0.18, 0.95)
            }
            self.agents.append(agent)
        self.history = []
    def update_market_and_socio(self):
        self.market_cond["fear_index"] = min(1.0, max(0.0, self.market_cond["fear_index"] + random.uniform(-0.1, 0.1)))
        self.market_cond["liquidity"] = min(1.0, max(0.0, self.market_cond["liquidity"] + random.uniform(-0.05, 0.05)))
        self.market_cond["volatility"] = min(1.0, max(0.0, self.market_cond["volatility"] + random.uniform(-0.07, 0.07)))
        self.socio_state.update()
    def one_turn(self, turn_index):
        self.update_market_and_socio()
        logs = []
        actions = []
        for agent in self.agents:
            agent_logs, agent_actions = agent.take_turn(self.socio_state, self.market_cond, turn_index)
            logs += agent_logs
            actions += agent_actions
        self.history.append({
            "logs": logs,
            "actions": actions,
            "socio": {
                "unemployment_rate": self.socio_state.unemployment_rate,
                "inflation_rate": self.socio_state.inflation_rate,
                "consumption_index": self.socio_state.consumption_index
            },
            "market": dict(self.market_cond)
        })
    def total_market_value(self):
        value = 0
        for agent in self.agents:
            value += agent.cash
            for asset in agent.assets.values():
                value += asset.value
        return value

class MultiAgentPortfolioSimulatorGUI:
    LOG_COLORS = {
        'info': 'black', 'agent': 'purple', 'trade': 'green', 'socio': 'brown', 'event': 'blue'
    }
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Agent Sun Tzu Chess + Socio-Economic Portfolio Simulator")
        self.state = MultiAgentPortfolio()
        self.log_text = ScrolledText(root, state='disabled', width=120, height=20, wrap='word')
        self.log_text.pack(padx=10, pady=5)
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)
        tk.Label(control_frame, text="Number of Turns:").grid(row=0, column=0, padx=5)
        self.turns_var = tk.IntVar(value=12)
        self.turns_entry = tk.Entry(control_frame, width=5, textvariable=self.turns_var)
        self.turns_entry.grid(row=0, column=1)
        self.run_button = tk.Button(control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=0, column=2, padx=5)
        self.export_button = tk.Button(control_frame, text="Export Report", command=self.export_report, state='disabled')
        self.export_button.grid(row=0, column=3, padx=5)

    def log(self, message, event_type="info"):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n", event_type)
        self.log_text.tag_config(event_type, foreground=self.LOG_COLORS.get(event_type, 'black'))
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()

    def run_simulation(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
        self.log("=== Multi-Agent + Sun Tzu Chess + Socio-Economic Simulation Started ===", event_type="event")
        try:
            turns = int(self.turns_var.get())
            assert turns > 0
        except Exception:
            messagebox.showerror("Error", "Invalid number of turns.")
            return
        for k in range(turns):
            self.state.one_turn(k+1)
            st = self.state.socio_state
            self.log(f"Turn {k+1} - Socio: unemployment={st.unemployment_rate:.3f}, inflation={st.inflation_rate:.3f}, consumption_index={st.consumption_index:.2f}", event_type="socio")
            for log_msg in self.state.history[-1]["logs"]:
                self.log(log_msg, event_type="agent")
        self.log(f"\nTotal market value: ${self.state.total_market_value():.2f}", event_type="event")
        self.log("\n=== Simulation Completed ===", event_type="event")
        self.export_button.config(state='normal')

    def export_report(self):
        if not self.state.history:
            messagebox.showwarning("No Data", "No data to export.")
            return
        filename = f"multiagent_portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, "w") as f:
                json.dump(self.state.history, f, indent=2)
            self.log(f"Report exported to: {filename}", event_type="event")
            messagebox.showinfo("Export Complete", f"Report saved as:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiAgentPortfolioSimulatorGUI(root)
    root.mainloop()
