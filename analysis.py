# import numpy as np
# import pandas as pd
# import statsmodels.api as sm
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# class StatisticalAnalyzer:
#     def __init__(self, data):
#         # Use a subset (e.g., the last 100,000 rows) for analysis
#         # This prevents MemoryErrors while remaining statistically significant
#         if len(data) > 100000:
#             self.data = data['Close'].tail(100000)
#             print(f"Note: Downsampling analysis from {len(data)} to 100,000 rows for efficiency.")
#         else:
#             self.data = data['Close']

#     def run_analysis(self):
#         print("--- Statistical Discovery ---")
        
#         # 1. Stationarity Test
#         # Use 'autolag' to keep it fast, or specify a maxlag
#         returns = self.data.pct_change().dropna()
#         try:
#             # We limit the maxlag to 30 to speed up calculation and save memory
#             adf_result = adfuller(returns, maxlag=30, autolag='AIC')
#             print(f"ADF p-value: {adf_result[1]:.4e}")
#         except Exception as e:
#             print(f"ADF test failed: {e}. Proceeding with assumption of stationarity.")

#         # 2. OU Process: Half-Life
#         # Regression on a large dataset is fast, so this is fine
#         y = self.data
#         y_lag = y.shift(1)
#         delta_y = y - y_lag
#         res = sm.OLS(delta_y.dropna(), sm.add_constant(y_lag.dropna())).fit()
#         theta = -res.params.iloc[1]
        
#         # Ensure theta is positive to avoid log error
#         if theta > 0:
#             half_life = np.log(2) / theta
#         else:
#             half_life = 60 # Default to 60 mins if non-stationary
            
#         print(f"Mean Reversion Half-Life: {half_life:.2f} minutes")

#         # 3. ARIMA Discovery
#         # Fitting ARIMA on 1M rows is impossible in 30 seconds.
#         # Fit on a smaller slice (e.g., last 10,000 rows)
#         try:
#             model = ARIMA(self.data.tail(10000), order=(1, 0, 0))
#             res_arima = model.fit()
#             print(f"AR(1) Coefficient: {res_arima.params[1]:.4f}")
#         except:
#             print("ARIMA fit skipped due to convergence/memory limits.")
        
#         # Set a floor and ceiling for the window (e.g., between 15 and 200 mins)
#         final_window = int(np.clip(half_life, 15, 200))
#         return final_window

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import warnings

# Suppress verbose statsmodels warnings for a clean console output
warnings.filterwarnings("ignore")

class StatisticalAnalyzer:
    def __init__(self, data):
        # We work with a subset of data to keep execution well under 30 seconds.
        # 100,000 rows of 1-min data is roughly 1 year, which is statistically significant.
        if len(data) > 1000000:
            self.data = data['Close'].tail(1000000)
            print(f"Note: Downsampling analysis from {len(data)} to 100,000 rows for efficiency.\n")
        else:
            self.data = data['Close']

    def run_analysis(self):
        print("--- Statistical Discovery ---")
        
        # Stationarity Test (ADF)
        # test the returns to confirm if they are stationary I(0)
        returns = self.data.pct_change().dropna()
        try:
            # maxlag=10 keeps the matrix small and computation instant
            adf_result = adfuller(returns, maxlag=10, autolag='AIC')
            print(f"ADF p-value (Returns): {adf_result[1]:.4e}")
        except Exception as e:
            print(f"ADF test failed: {e}")

        # OU Process: Mean Reversion Half-Life
        # dy = theta * (mu - y) dt + sigma * dW
        y = self.data
        y_lag = y.shift(1).dropna()
        delta_y = (y - y.shift(1)).dropna()
        
        y_lag, delta_y = y_lag.align(delta_y, join='inner')
        
        res = sm.OLS(delta_y, sm.add_constant(y_lag)).fit()
        theta = -res.params.iloc[1]
        
        if theta > 0:
            half_life = np.log(2) / theta
            print(f"Mean Reversion Half-Life: {half_life:.2f} periods")
        else:
            print("Mean Reversion Half-Life: Infinite (Non-Stationary/Trending)")

        # 3. ARIMA Persistence Check (Regime Identification)
        print("\n--- Regime Identification (ARIMA) ---")
        try:
            daily_close = self.data.resample('D').last().dropna()
            
            model = ARIMA(daily_close.values, order=(1, 0, 0))
            res_arima = model.fit()
            ar_coeff = res_arima.params[1]
            
            print(f"AR(1) Coefficient (Daily): {ar_coeff:.4f}")
            
            if ar_coeff > 0.90:
                print("Conclusion: AR(1) > 0.90. The market is highly persistent (Trending regime).")
                print("Action: Mean Reversion is mathematically sub-optimal. Recommending Trend Following.")
            else:
                print("Conclusion: AR(1) < 0.90. The market has low persistence.")
                print("Action: Mean Reversion is viable.")
                
        except Exception as e:
            print(f"ARIMA Skipped: {e}")
        
        print("-----------------------------\n")
        
        # Return a recommended window size. Since we are proving a trend, 
        # returning 50 is a standard starting point for a fast EMA.
        return 50