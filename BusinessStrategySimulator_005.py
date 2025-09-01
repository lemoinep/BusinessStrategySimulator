# Author(s): Dr. Patrick Lemoine
# Sun Tzu The Art of Investment War in real time

# This program is an interactive stock portfolio simulator that applies Sun Tzu’s strategic principles to modern financial markets. 
# It uses real-time market data and an adaptive AI to provide tactical buy and sell recommendations. 
# The simulator helps users improve investment decision-making by blending ancient wisdom with contemporary trading challenges.

import random
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import json
import numpy as np
import yfinance as yf

# Price retrieval with pandas iloc to avoid warning
def get_stock_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        price = data['Close'].iloc[-1]
        return price
    except Exception:
        simulated_prices = {
            'AAPL': random.uniform(140, 170),
            'GOOG': random.uniform(2500, 3000),
            'TSLA': random.uniform(700, 900),
            'MSFT': random.uniform(280, 350),
            'SPY': random.uniform(400, 450)
        }
        return simulated_prices.get(ticker, random.uniform(100, 1000))

class AssetType:
    def __init__(self, name, ticker, quantity, volatility, liquidity, special=None):
        self.name = name
        self.ticker = ticker
        self.quantity = quantity
        self.volatility = volatility
        self.liquidity = liquidity
        self.special = special or {}
        self.buy_date = None
        self.buy_value = None

    @property
    def price(self):
        return get_stock_price(self.ticker)

    @property
    def value(self):
        return self.quantity * self.price

class SunTzuMarketAI:
    def __init__(self, personality, memory_len=5):
        self.personality = personality
        self.memory_len = memory_len
        self.memory = []
        self.last_allocation = [0.5, 0.2, 0.1, 0.1, 0.1]

    def observe_outcome(self, beat_market, portfolio_dist):
        self.memory.append({'beat_market': beat_market, 'portfolio_dist': portfolio_dist})
        if len(self.memory) > self.memory_len:
            self.memory.pop(0)
        self.last_allocation = portfolio_dist

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

    def adjust_market_conditions(self, market_sentiment, portfolio_perf):
        self.decide_personality()
        return {
            "volatile": self.personality == "sideways",
            "strong_drop": self.personality == "bearish",
            "surprise_rally": self.personality == "bullish" and random.random() < 0.15
        }

class PortfolioState:
    def __init__(self):
        self.assets = []
        self.cash = 0
        self.market_ai = SunTzuMarketAI(personality=random.choice(["bullish", "bearish", "sideways"]))
        self.risk_aversion = 0.7
        self.portfolio_history = []
        self.market_cond = {
            "fear_index": random.uniform(0.1, 0.9),
            "liquidity": random.uniform(0.5, 1.0),
            "volatility": random.uniform(0.1, 0.4)
        }

    def init_portfolio(self, cash=10000, stocks=None):
        if stocks is None:
            stocks = [
                {"name":"Apple","ticker":"AAPL","quantity":20},
                {"name":"Google","ticker":"GOOG","quantity":3},
                {"name":"Tesla","ticker":"TSLA","quantity":8},
                {"name":"Microsoft","ticker":"MSFT","quantity":10},
                {"name":"S&P 500 ETF","ticker":"SPY","quantity":10}
            ]
            self.cash = cash
            self.assets = []
            for s in stocks:
                at = AssetType(s['name'], s['ticker'], s['quantity'], 0.2, 0.9)
                self.assets.append(at)
        else:
            self.cash = cash
            self.assets = []
            for s in stocks:
                at = AssetType(s['name'], s['ticker'], s['quantity'], 0.2, 0.9)
                at.buy_date = s.get('buy_date')
                at.buy_value = s.get('buy_value')
                self.assets.append(at)

    def load_portfolio_from_file(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.init_portfolio(cash=data.get('cash', 10000), stocks=data.get('stocks', []))

    def save_portfolio_to_file(self, filepath):
        stocks_data = []
        for asset in self.assets:
            stocks_data.append({
                'name': asset.name,
                'ticker': asset.ticker,
                'quantity': asset.quantity,
                'buy_date': asset.buy_date,
                'buy_value': asset.buy_value
            })
        data = {'cash': self.cash, 'stocks': stocks_data}
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def total_value(self):
        return self.cash + sum(a.value for a in self.assets)

    def asset_allocation(self):
        tv = self.total_value()
        return [a.value / tv for a in self.assets]

    def update_market_conditions(self):
        self.market_cond["fear_index"] = min(1.0, max(0.0, self.market_cond["fear_index"] + random.uniform(-0.1, 0.1)))
        self.market_cond["liquidity"] = min(1.0, max(0.0, self.market_cond["liquidity"] + random.uniform(-0.05, 0.05)))
        self.market_cond["volatility"] = min(1.0, max(0.0, self.market_cond["volatility"] + random.uniform(-0.07, 0.07)))

    def market_index_perf(self):
        return get_stock_price('SPY')

def sun_tzu_market_strategy(asset, fear_index, volatility, liquidity, cash_available, current_turn):
    recommendations = []
    price = asset.price
    if fear_index > 0.7 and liquidity > 0.5 and cash_available > price:
        recommendations.append(f"Buy more {asset.ticker}: market is fearful, opportunity to attack.")
    elif volatility > 0.6 and asset.quantity > 0:
        recommendations.append(f"Consider selling part of {asset.ticker}: market is volatile, reduce risk.")
    elif liquidity < 0.4:
        recommendations.append(f"Hold cash, liquidity is low: avoid aggressive moves.")
    if current_turn % 5 == 0:
        recommendations.append(f"Reassess strategy for {asset.ticker} on turn {current_turn}.")
    return recommendations

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class PortfolioSimulatorGUI:
    LOG_COLORS = {
        'info': 'black', 'win': 'blue', 'loss': 'red',
        'trade': 'green', 'ai': 'purple', 'event': 'brown'
    }
    def __init__(self, root):
        self.root = root
        self.root.title("Sun Tzu Stock Portfolio Simulator")
        self.state = PortfolioState()
        self.log_text = ScrolledText(root, state='disabled', width=110, height=20, wrap='word')
        self.log_text.pack(padx=10, pady=5)
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="Number of Turns:").grid(row=0, column=0, padx=5)
        self.turns_var = tk.IntVar(value=12)
        self.turns_entry = tk.Entry(control_frame, width=5, textvariable=self.turns_var)
        self.turns_entry.grid(row=0, column=1)

        tk.Label(control_frame, text="Allocation % (AAPL/GOOG/TSLA/MSFT/SPY) - e.g. 30/20/10/20/20:").grid(row=1, column=0)
        self.alloc_var = tk.StringVar(value="30/20/10/20/20")
        self.alloc_entry = tk.Entry(control_frame, width=20, textvariable=self.alloc_var)
        self.alloc_entry.grid(row=1, column=1)

        self.run_button = tk.Button(control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=0, column=2, padx=5)

        self.export_button = tk.Button(control_frame, text="Export Report", command=self.export_report, state='disabled')
        self.export_button.grid(row=0, column=3, padx=5)

        self.load_button = tk.Button(control_frame, text="Load Portfolio", command=self.load_portfolio)
        self.load_button.grid(row=1, column=2, padx=5)

        self.save_button = tk.Button(control_frame, text="Save Portfolio", command=self.save_portfolio)
        self.save_button.grid(row=1, column=3, padx=5)

        self.logs = []
        self.sim_data = []

    def log(self, message, event_type="info"):
        self.logs.append(message)
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n", event_type)
        self.log_text.tag_config(event_type, foreground=self.LOG_COLORS.get(event_type, 'black'))
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()

    def parse_allocation(self, dist):
        try:
            result = [int(x) for x in dist.strip().split('/')]
        except:
            result = [30,20,10,20,20]
        total = sum(result)
        if total != 100 and total > 0:
            ratio = [x*100//total for x in result]
            return ratio + [0]*(5 - len(ratio))
        return result + [0]*(5 - len(result))

    def portfolio_turn(self, alloc_dist):
        self.state.update_market_conditions()
        self.log(f"\n--- Turn {len(self.sim_data)+1} ---", event_type="info")
        alloc_perc = [x/100 for x in alloc_dist]
        portfolio_value_before = self.state.total_value()
        market_index_start = self.state.market_index_perf()

        all_recommendations = []
        for asset in self.state.assets:
            recs = sun_tzu_market_strategy(asset,
                                           self.state.market_cond['fear_index'],
                                           self.state.market_cond['volatility'],
                                           self.state.market_cond['liquidity'],
                                           self.state.cash,
                                           len(self.sim_data)+1)
            all_recommendations.extend(recs)
            for r in recs:
                self.log("Strategy Advice: " + r, event_type="event")

        total_value = self.state.total_value()
        for i, asset in enumerate(self.state.assets):
            target_value = total_value * alloc_perc[i]
            qty_target = target_value / asset.price if asset.price > 0 else 0
            diff_qty = int(qty_target - asset.quantity)
            if diff_qty > 0:
                cost = diff_qty * asset.price
                if cost <= self.state.cash:
                    self.state.cash -= cost
                    asset.quantity += diff_qty
                    self.log(f"Bought {diff_qty} {asset.ticker}.", event_type="trade")
            elif diff_qty < 0:
                revenue = -diff_qty * asset.price
                self.state.cash += revenue
                asset.quantity += diff_qty
                self.log(f"Sold {-diff_qty} {asset.ticker}.", event_type="trade")

        ai_react = self.state.market_ai.adjust_market_conditions(
            self.state.market_cond, portfolio_value_before)
        if ai_react['strong_drop']:
            self.log("Market drops sharply! Your aggressive positions suffer!", event_type="loss")
            for asset in self.state.assets:
                drop = random.uniform(0.05, 0.15)
                if random.random() < 0.8:
                    asset.quantity = max(0, int(asset.quantity * (1 - drop)))
        if ai_react['surprise_rally']:
            self.log("Sudden rally: Weak positions surge!", event_type="win")
            for asset in self.state.assets:
                gain = random.uniform(0.04, 0.09)
                if random.random() < 0.7:
                    asset.quantity = int(asset.quantity * (1 + gain))

        new_value = self.state.total_value()
        market_index_end = self.state.market_index_perf()
        beat_market = (new_value - portfolio_value_before) > (market_index_end - market_index_start)
        self.state.market_ai.observe_outcome(beat_market, self.state.asset_allocation())
        self.state.market_ai.decide_personality()

        self.log(f"Total portfolio value: ${new_value:.2f} (Cash: ${self.state.cash:.2f})", event_type="info")
        for asset in self.state.assets:
            self.log(f"  {asset.ticker}: {asset.quantity} units @ ${asset.price:.2f} each, Total=${asset.value:.2f}", event_type="info")

        self.sim_data.append({
            "turn": len(self.sim_data)+1,
            "portfolio_value": new_value,
            "cash": self.state.cash,
            "market_fear": self.state.market_cond['fear_index'],
            "market_liquidity": self.state.market_cond['liquidity'],
            "market_volatility": self.state.market_cond['volatility'],
            "ai_personality": self.state.market_ai.personality,
            "tactics": all_recommendations,
            "beat_market": beat_market
        })

    def run_simulation(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
        self.logs.clear()
        self.sim_data.clear()
        self.state.init_portfolio()
        try:
            turns = int(self.turns_var.get())
            assert turns > 0
        except Exception:
            messagebox.showerror("Error", "Invalid number of turns.")
            return
        alloc_dist = self.parse_allocation(self.alloc_var.get())
        self.log("=== Starting Sun Tzu Stock Portfolio Simulation ===", event_type="info")
        for _ in range(turns):
            self.portfolio_turn(alloc_dist)
            if self.state.total_value() <= 0:
                self.log("Portfolio completely lost. Simulation ends.", event_type="loss")
                break
        self.log("\n=== Simulation Ended ===", event_type="event")
        self.export_button.config(state='normal')

    def export_report(self):
        if not self.sim_data:
            messagebox.showwarning("No Data", "No data to export.")
            return
        filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(self.sim_data, f, indent=2, cls=NumpyEncoder)
        self.log(f"Report exported to: {filename}", event_type="event")
        messagebox.showinfo("Export Complete", f"Report saved as:\n{filename}")

    def load_portfolio(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Files","*.json")])
        if file:
            try:
                self.state.load_portfolio_from_file(file)
                self.log(f"Portfolio loaded from {file}", event_type="event")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load portfolio:\n{e}")

    def save_portfolio(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files","*.json")])
        if file:
            try:
                self.state.save_portfolio_to_file(file)
                self.log(f"Portfolio saved to {file}", event_type="event")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save portfolio:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioSimulatorGUI(root)
    root.mainloop()
