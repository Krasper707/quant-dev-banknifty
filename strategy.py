import numpy as np
import pandas as pd

# class MeanReversionStrategy:
#     def __init__(self, window=20, entry_z=2.0, exit_z=0.5):
#         self.window = window
#         self.entry_z = entry_z
#         self.exit_z = exit_z

#     def generate_signals(self, df):
#         # 1. Calculate Indicators (Vectorized)
#         df['rolling_mean'] = df['Close'].rolling(window=self.window).mean()
#         df['rolling_std'] = df['Close'].rolling(window=self.window).std()
#         df['z_score'] = (df['Close'] - df['rolling_mean']) / df['rolling_std']
        
#         # 2. Generate Target Positions
#         # 1 = Long, -1 = Short, 0 = Flat
#         df['signal'] = 0
        
#         # Entry Logic
#         df.loc[df['z_score'] < -self.entry_z, 'signal'] = 1   # Buy oversold
#         df.loc[df['z_score'] > self.entry_z, 'signal'] = -1  # Sell overbought
        
#         # Exit Logic: Reversion to mean (Z-score near 0)
#         # This is a slightly more complex vectorized way to handle "hold until mean"
#         # For a simple version:
#         df.loc[df['z_score'].abs() < self.exit_z, 'signal'] = 0
        
#         # 3. Forward fill signals to maintain position until an exit is hit
#         # (This avoids flickering)
#         df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        
#         # 4. Filter for Market Hours (Close all positions at 15:15)
#         df.loc[df.index.time >= pd.to_datetime('15:15').time(), 'position'] = 0
        
#         return df

#"""
#--- Strategy Performance ---
#Total Return: -94.98%
#Sharpe Ratio: -1.49
#Max Drawdown: -95.30%
#Win Rate: 31.74%
#"""

class MeanReversionStrategy:
    def __init__(self, window=20, entry_z=2.0):
        self.window = window
        self.entry_z = entry_z

    def generate_signals(self, df):
        # 1. Indicators on 15-minute bars
        df['rolling_mean'] = df['Close'].rolling(window=self.window).mean()
        df['rolling_std'] = df['Close'].rolling(window=self.window).std()
        df['z_score'] = (df['Close'] - df['rolling_mean']) / df['rolling_std']
        
        # 2. Logic: Hysteresis (Wait for a clear signal)
        df['position'] = 0
        df.loc[df['z_score'] > self.entry_z, 'position'] = -1
        df.loc[df['z_score'] < -self.entry_z, 'position'] = 1
        
        # Stay in the trade until it returns to the mean (0)
        df['position'] = df['position'].replace(0, np.nan).ffill().fillna(0)
        
        # Exit rules
        df.loc[(df['position'] == 1) & (df['z_score'] >= 0), 'position'] = 0
        df.loc[(df['position'] == -1) & (df['z_score'] <= 0), 'position'] = 0
        
        return df
    

class MomentumStrategy:
    def __init__(self, fast_window=50, slow_window=200):
        # On 15-min bars: Fast = ~2 Days, Slow = ~8 Days
        self.fast_window = fast_window
        self.slow_window = slow_window

    # def generate_signals(self, df):
    #     # 1. Calculate EMAs
    #     df['fast_ema'] = df['Close'].ewm(span=self.fast_window, adjust=False).mean()
    #     df['slow_ema'] = df['Close'].ewm(span=self.slow_window, adjust=False).mean()
        
    #     # 2. Generate Signals
    #     df['signal'] = 0
    #     df.loc[df['fast_ema'] > df['slow_ema'], 'signal'] = 1
    #     df.loc[df['fast_ema'] < df['slow_ema'], 'signal'] = -1
        
    #     # 3. Position Sizing
    #     df['position'] = df['signal']        
        
    #     return df
    def generate_signals(self, df):
        # 1. EMAs
        df['fast_ema'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['slow_ema'] = df['Close'].ewm(span=30, adjust=False).mean()
        
        # Robust Volatility Filter 
        df['volatility'] = df['Close'].pct_change().rolling(20).std()
        # Calculate the median volatility over the last few days to set a baseline
        vol_threshold = df['volatility'].rolling(200).median()
        
        # Entry Logic
        df['signal'] = 0
        
        # Condition: EMAs cross AND volatility is above the median (market is active)
        df.loc[(df['fast_ema'] > df['slow_ema']) & (df['volatility'] > vol_threshold), 'signal'] = 1
        df.loc[(df['fast_ema'] < df['slow_ema']) & (df['volatility'] > vol_threshold), 'signal'] = -1
        
        # Persistence & Exit
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        
        # Exit if the trend reverses (Standard crossover exit)
        df.loc[(df['position'] == 1) & (df['fast_ema'] < df['slow_ema']), 'position'] = 0
        df.loc[(df['position'] == -1) & (df['fast_ema'] > df['slow_ema']), 'position'] = 0
        
        return df