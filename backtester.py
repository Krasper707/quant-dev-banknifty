import numpy as np
import pandas as pd

class VectorizedBacktester:
    def __init__(self, initial_capital=100000, tc=0.0001, slippage=0.00005):
        self.initial_capital = initial_capital
        self.tc = tc  # 0.01%
        self.slippage = slippage # 0.005%

    def run(self, df):
        df['asset_returns'] = df['Close'].pct_change()
        df['actual_position'] = df['position'].shift(1).fillna(0)
        
        # Calculate Strategy Returns
        df['strat_returns_raw'] = df['actual_position'] * df['asset_returns']
        
        # Calculate Transaction Costs & Slippage
        df['trades'] = df['actual_position'].diff().abs()
        df['costs'] = df['trades'] * (self.tc + self.slippage)
        
        # Net Returns
        df['strat_returns_net'] = df['strat_returns_raw'] - df['costs']
        
        # Equity Curve
        df['equity_curve'] = (1 + df['strat_returns_net']).cumprod() * self.initial_capital
        num_trades = df['trades'].sum()
        print(f"Total Trades Executed: {num_trades}")

        
        return self.calculate_metrics(df)
    def calculate_metrics(self, df):
        total_return = (df['equity_curve'].iloc[-1] / self.initial_capital) - 1
        days_in_data = (df.index.max() - df.index.min()).days
        years = days_in_data / 365.25
        annualized_return = ((1 + total_return) ** (1 / years)) - 1 if years > 0 else 0
        
        # Sharpe Ratio
        ann_factor = 252 * 25 
        daily_returns = df['strat_returns_net']
        sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(ann_factor)
        
        # Max Drawdown
        rolling_max = df['equity_curve'].cummax()
        drawdown = (df['equity_curve'] - rolling_max) / rolling_max
        max_dd = drawdown.min()
        
        
        # Identify blocks where a position is held
        # A new trade starts whenever the position changes
        df['trade_id'] = (df['position'] != df['position'].shift(1)).cumsum()
        
        # Filter only rows where we actually have a position
        trade_data = df[df['position'] != 0].copy()
        
        if not trade_data.empty:
            # Group by trade_id to get the total PnL per trade
            trade_pnl = trade_data.groupby('trade_id')['strat_returns_net'].sum()
            
            # Group by trade_id to get the duration (number of 15-min bars)
            trade_durations = trade_data.groupby('trade_id').size()
            
            win_rate = (trade_pnl > 0).mean()
            avg_trade_duration = trade_durations.mean() * 15 # Convert bars to minutes
        else:
            win_rate = 0
            avg_trade_duration = 0

        metrics = {
            "Total Return": f"{total_return:.2%}",
            "Annualized Return": f"{annualized_return:.2%}",
            "Sharpe Ratio": f"{sharpe:.2f}",
            "Max Drawdown": f"{max_dd:.2%}",
            "Win Rate": f"{win_rate:.2%}",
            "Avg Trade Duration": f"{avg_trade_duration:.0f} minutes"
        }
        return metrics, df