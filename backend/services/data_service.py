import yfinance as yf
import pandas as pd


def get_stock_history(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    """

    try:
        symbol = symbol.upper()

        if not symbol.endswith(".NS"):
            symbol += ".NS"

        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
        )

        if df.empty:
            return pd.DataFrame()

        # Fix MultiIndex columns returned by yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df

    except Exception as e:
        print(e)
        return pd.DataFrame()