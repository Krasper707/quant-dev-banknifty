import matplotlib.pyplot as plt
import os
import pandas as pd

def save_performance_plots(df, folder='results'):
    # 1. Create results directory if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Use a clean style
    plt.style.use('ggplot')

    # --- PLOT 1: Price and EMAs (Close-up of last 1000 bars) ---
    plt.figure(figsize=(15, 7))
    subset = df.tail(100000) 
    plt.plot(subset.index, subset['Close'], label='BankNifty Price', color='black', alpha=0.3)
    plt.plot(subset.index, subset['fast_ema'], label='50 EMA (Fast)', color='blue', linewidth=1.5)
    plt.plot(subset.index, subset['slow_ema'], label='200 EMA (Slow)', color='red', linewidth=1.5)
    plt.title('BankNifty Price vs. EMAs (Close-up View)')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{folder}/price_ema_crossover.png')
    plt.close()

    # --- PLOT 2: Equity Curve & Drawdown (Full History) ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True, 
                                   gridspec_kw={'height_ratios': [3, 1]})

    # Equity Curve
    ax1.plot(df.index, df['equity_curve'], color='green', linewidth=1.5)
    ax1.set_title('Strategy Equity Curve (9-Year Performance)')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.grid(True)

    # Drawdown Chart
    # Calculate drawdown series
    rolling_max = df['equity_curve'].cummax()
    drawdown = (df['equity_curve'] - rolling_max) / rolling_max
    
    ax2.fill_between(df.index, drawdown, 0, color='red', alpha=0.3)
    ax2.plot(df.index, drawdown, color='red', linewidth=0.5)
    ax2.set_title('Drawdown Profile')
    ax2.set_ylabel('Drawdown %')
    ax2.set_xlabel('Date')
    ax2.grid(True)
    plt.figure(figsize=(15, 7))
    subset = df.tail(1000).copy() # Last ~2 months
    
    plt.plot(subset.index, subset['Close'], label='BankNifty Price', color='black', alpha=0.3)
    plt.plot(subset.index, subset['fast_ema'], label='50 EMA', color='blue', linewidth=1.5)
    plt.plot(subset.index, subset['slow_ema'], label='200 EMA', color='red', linewidth=1.5)
    
    # Extract Buy/Sell signals to plot markers
    # A trade occurs when 'actual_position' changes
    subset['pos_change'] = subset['actual_position'].diff()
    
    buys = subset[subset['pos_change'] == 2.0]  # Went from -1 to 1
    sells = subset[subset['pos_change'] == -2.0] # Went from 1 to -1
    initial_buys = subset[(subset['pos_change'] == 1.0) & (subset['actual_position'] == 1)]
    initial_sells = subset[(subset['pos_change'] == -1.0) & (subset['actual_position'] == -1)]
    
    # Plot Green Up Arrows for Buys
    plt.scatter(buys.index, buys['Close'], marker='^', color='green', s=100, label='Buy Signal')
    plt.scatter(initial_buys.index, initial_buys['Close'], marker='^', color='green', s=100)
    
    # Plot Red Down Arrows for Sells
    plt.scatter(sells.index, sells['Close'], marker='v', color='red', s=100, label='Sell Signal')
    plt.scatter(initial_sells.index, initial_sells['Close'], marker='v', color='red', s=100)

    plt.title('BankNifty Price vs. EMAs with Trading Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{folder}/price_signals_chart.png')
    plt.close()

    plt.tight_layout()
    plt.savefig(f'{folder}/equity_drawdown_analysis.png')
    plt.close()
    
    print(f"Plots saved successfully in the /{folder} directory.")