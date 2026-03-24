from data_loader import MarketDataLoader
from analysis import StatisticalAnalyzer
from strategy import MeanReversionStrategy , MomentumStrategy

from backtester import VectorizedBacktester
from visualizer import save_performance_plots

# 1. Load & Clean
loader = MarketDataLoader('banknifty_candlestick_data.csv')
df = loader.load_and_clean()

# 2. Analyze (Statistical Justification)
analyzer = StatisticalAnalyzer(df)
best_window = analyzer.run_analysis() # Returns half-life

# 3. Strategy (Apply Signals)
# We use the half-life from our OU process as the window
strat = MomentumStrategy(fast_window=10, slow_window=30)
df = strat.generate_signals(df)

# 4. Backtest
bt = VectorizedBacktester()
metrics, results_df = bt.run(df)

save_performance_plots(results_df)

print("\n--- Strategy Performance ---")
for k, v in metrics.items():
    print(f"{k}: {v}")

# 5. Save/Plot
# results_df['equity_curve'].plot()