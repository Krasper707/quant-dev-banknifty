import pandas as pd
import numpy as np

class MarketDataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_and_clean(self):
        df = pd.read_csv(self.file_path)
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d-%m-%Y %H:%M:%S')
        df = df.sort_values('datetime').set_index('datetime')
        df = df.drop(columns=['Date', 'Time'])
        df = df[~df.index.duplicated(keep='first')]
        full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='min')
        df = df.reindex(full_range)
        df['Close'] = df['Close'].ffill().bfill()        
        df['Close'] = self._remove_outliers(df['Close'])
        # 6. Keep only market hours
        df = df.between_time('09:15', '15:30')
       # Convert 1-minute noise into 15-minute professional bars
        # 'OHLC' tells pandas how to aggregate the price
        df = df['Close'].resample('15min').ohlc()
        df = df['close'].to_frame() # We only need the closing price
        df = df.rename(columns={'close': 'Close'})
        df = df.dropna() # Remove gaps

        return df

    def _remove_outliers(self, series):
        # Robust outlier detection
        rolling_median = series.rolling(window=20).median()
        rolling_std = series.rolling(window=20).std()
        outlier_mask = (series - rolling_median).abs() > (5 * rolling_std)
        return series.where(~outlier_mask, rolling_median)

# Usage:
# loader = MarketDataLoader('data.csv')
# clean_data = loader.load_and_clean()