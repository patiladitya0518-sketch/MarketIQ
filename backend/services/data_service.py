import yfinance as yf
import pandas as pd


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    return symbol


def get_stock_history(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    """

    try:
        symbol = normalize_symbol(symbol)

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
        print(f"Historical data error: {e}")
        return pd.DataFrame()


def get_live_price(symbol: str):
    """
    Get the latest available market price for an NSE stock.

    Returns:
        float | None
    """

    try:
        symbol = normalize_symbol(symbol)

        ticker = yf.Ticker(symbol)

        # Try fast_info first
        try:
            price = ticker.fast_info.get("last_price")

            if price is not None:
                return round(float(price), 2)

        except Exception:
            pass

        # Fallback to recent intraday data
        df = ticker.history(
            period="1d",
            interval="1m",
        )

        if df.empty:
            return None

        price = df["Close"].dropna().iloc[-1]

        return round(float(price), 2)

    except Exception as e:
        print(f"Live price error for {symbol}: {e}")
        return None