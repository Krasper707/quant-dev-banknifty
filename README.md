
# Quantitative Strategy Report: BankNifty Momentum

**Candidate:** Karthik Murali M  
**Strategy Class:** Time-Series Momentum (Trend Following)  
**Timeframe:** 15-Minute Resampled Intraday/Swing

---

## 1. Executive Summary

This project implements a systematic momentum strategy for BankNifty. While initial exploration focused on Mean Reversion (MR), statistical testing via **ADF** and **ARIMA** models revealed a highly persistent, non-stationary regime ($I(1)$) where MR was mathematically sub-optimal. The final system utilizes a dual-EMA crossover on resampled 15-minute bars, achieving a **Total Return of 274.69%** and a **Sharpe Ratio of 0.63** over a 9-year backtest, after accounting for transaction costs and slippage.

---

## 2. Data Engineering & Robustness

The provided dataset contained ~1.2M rows of minute-level data for a single asset (BankNifty).

### 2.1 Data Integrity

- **Gap Handling:** Identified 3,605 missing intraday minutes. I implemented a programmatic reindexing to a 1-minute grid and utilized **Forward-Filling (ffill)** to represent the last tradable price, ensuring zero lookahead bias.
- **Outlier Mitigation:** Detected extreme returns (exceeding $\pm$ 7%). To ensure robustness against "fat-finger" errors and flash crashes, I implemented a **Rolling Median Absolute Deviation (MAD)** filter, capping returns at 6 standard deviations from the rolling median.
- **Resampling:** To improve the Signal-to-Noise ratio and meet the 30-second execution constraint, data was aggregated into **15-minute OHLC bars**.

---

## 3. Statistical Discovery & Regime Identification

To justify the strategy design, I conducted a three-tier statistical analysis:

- **Stationarity (ADF Test):** Price levels were found to be non-stationary, while returns were stationary ($p < 0.05$).
- **Mean Reversion Half-Life (OU Process):** Calculation of the Ornstein-Uhlenbeck half-life yielded $\approx$ 10,440 minutes. This indicated that mean reversion cycles are too slow for intraday execution and are dominated by macro trends.
- **Regime Identification (ARIMA):** An **ARIMA(1,0,0)** model was fitted to daily data. The **AR(1) coefficient of 0.9998** empirically proved a highly persistent "Random Walk with Drift" regime, indicating that momentum is the dominant factor in BankNifty.

---

## 4. Strategy Design & Evolution

### 4.1 The Pivot from Mean Reversion

Initial testing of a Z-score Mean Reversion strategy resulted in a **-100% return**. Analysis identified two failure points:

1.  **The Momentum Trap:** In a trending index, extreme Z-scores ($> 2.0$) act as breakout signals rather than reversion signals.
2.  **The "Fee Bleed":** Fading minute-level noise generated $\approx$ 73,000 trades, where transaction costs (0.01%) entirely eroded the capital.

### 4.2 Final Strategy: Tactical Momentum

The final strategy utilizes an **Exponential Moving Average (EMA) Crossover** (10-period Fast / 30-period Slow) on 15-minute bars.

- **Entry:** Fast EMA crosses above Slow EMA (Long) or below (Short).
- **Exit:** Contrary crossover (Trailing stop-loss effect).
- **Hold Period:** Swing (Multi-day).

---

## 5. Transaction Cost & Execution Analysis

A critical finding during research was the **Intraday "Fee Trap."**

Initially, I enforced a mandatory square-off at 15:15 IST to mitigate overnight risk. However, because BankNifty trends persist across days, this forced the system to exit and re-enter the same trend daily, generating $\approx$ 9,800 trades and a -80% return.

**Final Solution:** I pivoted to a **Swing Architecture** that allows overnight holding. This reduced the trade count by **90%** (from 9,879 to 4,179). By embracing overnight persistence, the "Alpha per Trade" significantly exceeded the transaction cost hurdle (0.01% fee + slippage), resulting in the final profitable equity curve.

---

#### Relationship Discovery

> **Relationship Discovered:**
> As the dataset provided contained only a single asset (BankNifty), cross-asset spread analysis (like Cointegration) was not applicable. Instead, I discovered a statistically meaningful relationship between **the asset's current price and its historical trend (Time-Series Autocorrelation)**.
>
> **Justification for Trading:**
> Using an **ARIMA(1,0,0)** model and **Augmented Dickey-Fuller (ADF)** stationarity testing, I identified an AR(1) coefficient of `0.9998`. This statistically proves a highly persistent, non-stationary market regime. This relationship is highly suitable for trading because it confirms that momentum (trend-following) carries a positive mathematical expectancy, whereas mean-reversion would result in negative expectancy.

#### Systematic Strategy Design

> **Strategy Rules:**
> Based on the ARIMA persistence discovery, the strategy is a Systematic Trend Follower executed on 15-minute resampled bars.
>
> - **Entry Signals:**
>   - Go LONG (+1) when Fast EMA (50) > Slow EMA (200).
>   - Go SHORT (-1) when Fast EMA (50) < Slow EMA (200).
> - **Exit Signals:**
>   - The strategy utilizes a continuous-in-market framework (always long or short). The exit signal for a Long is the entry signal for a Short (a moving average crossover).
> - **Position Sizing:**
>   - 100% Capital Allocation per trade (`Position = 1.0`). Fixed fractional sizing without leverage to ensure survival during drawdowns.
> - **Risk Controls:**
>   - The Slow EMA acts as a dynamic trailing stop-loss. By definition, if the market crashes against a Long position, the Fast EMA will cross below the Slow EMA, programmatically closing the Long and flipping to Short to protect capital.

---

## 6. Performance Evaluation

- **Total Return:** 274.69%
- **Sharpe Ratio:** 0.63
- **Max Drawdown:** -33.29%
- **Win Rate:** 32.76% (Typical for trend-following; winners $\gg$ losers).

### 6.1 Sensitivity Analysis

Comparison of two momentum regimes:

- **Macro-Trend (50/200 EMA):** Lower turnover (887 trades), Sharpe 0.37.
- **Tactical-Trend (10/30 EMA):** Higher turnover (4,179 trades), Sharpe 0.63.

**Conclusion:** The 10/30 EMA was selected as it optimally captures the 2–4 day swings characteristic of the BankNifty index while maintaining a healthy profit margin over transaction costs.

---

## 7. Limitations & Improvements

- **Market Impact:** The backtest assumes infinite liquidity. In reality, large positions in BankNifty might face higher slippage.
- **Risk Allocation:** Current sizing is a simple 1.0x levered position. Implementation of **Volatility Targeting** (Inverse-Vol Sizing) could further smooth the equity curve.
- **Alternative Filters:** Adding an ADX (Average Directional Index) filter could reduce whipsaws in sideways/non-trending markets.
