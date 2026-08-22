import yfinance as yf
import pandas as pd
from functools import lru_cache


# ============================================================
# MANUAL COMPANY → YAHOO SYMBOL
# ============================================================

COMPANY_SYMBOLS = {
    "RELIANCE": "RELIANCE.NS",
    "RELIANCE INDUSTRIES": "RELIANCE.NS",

    "TCS": "TCS.NS",
    "TATA CONSULTANCY SERVICES": "TCS.NS",

    "INFY": "INFY.NS",
    "INFOSYS": "INFY.NS",

    "HDFCBANK": "HDFCBANK.NS",
    "HDFC BANK": "HDFCBANK.NS",

    "ICICIBANK": "ICICIBANK.NS",
    "ICICI BANK": "ICICIBANK.NS",

    "SBIN": "SBIN.NS",
    "STATE BANK OF INDIA": "SBIN.NS",

    "WIPRO": "WIPRO.NS",

    "HCLTECH": "HCLTECH.NS",
    "HCL TECHNOLOGIES": "HCLTECH.NS",

    "LT": "LT.NS",
    "LARSEN AND TOUBRO": "LT.NS",
    "LARSEN & TOUBRO": "LT.NS",

    "ONGC": "ONGC.NS",

    "TITAN": "TITAN.NS",
    "TITAN COMPANY": "TITAN.NS",

    "DHTL": "DHTL.NS",
    "DHOOT TRANSMISSION": "DHTL.NS",
    "DHOOT TRANSMISSION INDIA": "DHTL.NS",

    "MILKYMIST": "MILKYMIST.NS",
    "MILKY MIST": "MILKYMIST.NS",
    "MILKY MIST DAIRY FOOD": "MILKYMIST.NS",
    "MILKY MIST DAIRY FOOD LIMITED": "MILKYMIST.NS",
    "MILKY MIST DAIRY FOODS": "MILKYMIST.NS",
}


# ============================================================
# NORMALIZE INPUT
# ============================================================

def clean_query(symbol: str) -> str:

    if not symbol:
        return ""

    return " ".join(
        str(symbol).strip().upper().split()
    )


# ============================================================
# DIRECT CANDIDATES
# ============================================================

def get_candidate_symbols(symbol: str):

    query = clean_query(symbol)

    if not query:
        return []

    # Already Yahoo format
    if query.endswith(".NS"):
        return [query]

    if query.endswith(".BO"):
        return [query]

    # Manual mapping
    if query in COMPANY_SYMBOLS:
        return [COMPANY_SYMBOLS[query]]

    # Unknown symbol:
    # NSE first, then BSE
    return [
        f"{query}.NS",
        f"{query}.BO",
    ]


# ============================================================
# CHECK WHETHER YAHOO SYMBOL EXISTS
# ============================================================

@lru_cache(maxsize=512)
def check_symbol(yahoo_symbol: str) -> bool:

    if not yahoo_symbol:
        return False

    try:

        ticker = yf.Ticker(yahoo_symbol)

        history = ticker.history(
            period="5d",
            interval="1d",
            timeout=10,
        )

        return (
            history is not None
            and not history.empty
        )

    except Exception as e:

        print(
            f"[MarketIQ] Symbol check failed "
            f"for {yahoo_symbol}: {e}"
        )

        return False


# ============================================================
# YAHOO FINANCE COMPANY SEARCH
#
# Important for:
# - New listings
# - Company names
# - Stocks not in COMPANY_SYMBOLS
# - NSE/BSE discovery
# ============================================================

@lru_cache(maxsize=256)
def search_stock_symbol(query: str):

    query = clean_query(query)

    if not query:
        return None

    # --------------------------------------------------------
    # Manual mapping first
    # --------------------------------------------------------

    if query in COMPANY_SYMBOLS:

        symbol = COMPANY_SYMBOLS[query]

        print(
            f"[MarketIQ] Mapping resolved: "
            f"{query} -> {symbol}"
        )

        return symbol

    # --------------------------------------------------------
    # Yahoo search
    # --------------------------------------------------------

    try:

        print(
            f"[MarketIQ] Automatic company search: "
            f"{query}"
        )

        search = yf.Search(
            query,
            max_results=20,
            news_count=0,
            enable_fuzzy_query=True,
        )

        quotes = search.quotes or []

        if not quotes:

            print(
                f"[MarketIQ] No Yahoo results for: "
                f"{query}"
            )

            return None

        indian_results = []

        for quote in quotes:

            yahoo_symbol = str(
                quote.get("symbol", "")
            ).upper()

            if not yahoo_symbol:
                continue

            quote_type = str(
                quote.get("quoteType", "")
            ).upper()

            exchange = str(
                quote.get("exchange", "")
            ).upper()

            exchange_display = str(
                quote.get("exchDisp", "")
            ).upper()

            # ------------------------------------------------
            # Only stocks/equities
            # ------------------------------------------------

            if quote_type and quote_type not in (
                "EQUITY",
                "STOCK",
            ):
                continue

            # ------------------------------------------------
            # Indian market detection
            # ------------------------------------------------

            is_indian = (
                yahoo_symbol.endswith(".NS")
                or yahoo_symbol.endswith(".BO")
                or exchange in ("NSI", "BSE")
                or "NSE" in exchange_display
                or "BSE" in exchange_display
            )

            if not is_indian:
                continue

            indian_results.append(quote)

        if not indian_results:

            print(
                f"[MarketIQ] No Indian equity found "
                f"for: {query}"
            )

            return None

        # ----------------------------------------------------
        # Prefer NSE
        # ----------------------------------------------------

        for quote in indian_results:

            yahoo_symbol = str(
                quote.get("symbol", "")
            ).upper()

            if yahoo_symbol.endswith(".NS"):

                print(
                    f"[MarketIQ] NSE search resolved: "
                    f"{query} -> {yahoo_symbol}"
                )

                return yahoo_symbol

        # ----------------------------------------------------
        # Otherwise BSE
        # ----------------------------------------------------

        for quote in indian_results:

            yahoo_symbol = str(
                quote.get("symbol", "")
            ).upper()

            if yahoo_symbol.endswith(".BO"):

                print(
                    f"[MarketIQ] BSE search resolved: "
                    f"{query} -> {yahoo_symbol}"
                )

                return yahoo_symbol

        return None

    except Exception as e:

        print(
            f"[MarketIQ] Yahoo search failed "
            f"for '{query}': {e}"
        )

        return None


# ============================================================
# RESOLVE STOCK
# ============================================================

@lru_cache(maxsize=512)
def resolve_symbol(symbol: str):

    query = clean_query(symbol)

    if not query:
        return None

    # --------------------------------------------------------
    # STEP 1 — Direct NSE/BSE candidates
    # --------------------------------------------------------

    candidates = get_candidate_symbols(query)

    for yahoo_symbol in candidates:

        if check_symbol(yahoo_symbol):

            print(
                f"[MarketIQ] Direct symbol resolved: "
                f"{query} -> {yahoo_symbol}"
            )

            return yahoo_symbol

    # --------------------------------------------------------
    # STEP 2 — Yahoo company search
    # --------------------------------------------------------

    searched_symbol = search_stock_symbol(query)

    if searched_symbol:

        if check_symbol(searched_symbol):

            print(
                f"[MarketIQ] Search symbol verified: "
                f"{query} -> {searched_symbol}"
            )

            return searched_symbol

    # --------------------------------------------------------
    # STEP 3 — Not found
    # --------------------------------------------------------

    print(
        f"[MarketIQ] Could not resolve stock: "
        f"{query}"
    )

    return None


# ============================================================
# VALIDATE SYMBOL
# ============================================================

def is_valid_symbol(symbol: str) -> bool:

    return resolve_symbol(symbol) is not None


# ============================================================
# HISTORICAL DATA
# ============================================================

def get_stock_history(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
) -> pd.DataFrame:

    yahoo_symbol = resolve_symbol(symbol)

    if not yahoo_symbol:

        print(
            f"[MarketIQ] Unable to resolve: "
            f"{symbol}"
        )

        return pd.DataFrame()

    try:

        print(
            f"[MarketIQ] Fetching history: "
            f"{yahoo_symbol}"
        )

        df = yf.download(
            yahoo_symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
            timeout=10,
            threads=False,
        )

        if df is None or df.empty:

            print(
                f"[MarketIQ] No historical data "
                f"for {yahoo_symbol}"
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # Fix MultiIndex
        # ----------------------------------------------------

        if isinstance(
            df.columns,
            pd.MultiIndex,
        ):

            df.columns = (
                df.columns
                .get_level_values(0)
            )

        # ----------------------------------------------------
        # Remove duplicates
        # ----------------------------------------------------

        df = df.loc[
            :,
            ~df.columns.duplicated()
        ]

        # ----------------------------------------------------
        # Required columns
        # ----------------------------------------------------

        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        for column in required_columns:

            if column not in df.columns:

                print(
                    f"[MarketIQ] Missing column "
                    f"{column} for "
                    f"{yahoo_symbol}"
                )

                return pd.DataFrame()

        # ----------------------------------------------------
        # Clean
        # ----------------------------------------------------

        df = df.dropna(
            subset=["Close"]
        )

        if df.empty:
            return pd.DataFrame()

        print(
            f"[MarketIQ] History loaded: "
            f"{yahoo_symbol} "
            f"({len(df)} candles)"
        )

        return df

    except Exception as e:

        print(
            f"[MarketIQ] Historical data error "
            f"for {yahoo_symbol}: {e}"
        )

        return pd.DataFrame()


# ============================================================
# LIVE PRICE
# ============================================================

def get_live_price(symbol: str):

    yahoo_symbol = resolve_symbol(symbol)

    if not yahoo_symbol:
        return None

    try:

        print(
            f"[MarketIQ] Fetching live price: "
            f"{yahoo_symbol}"
        )

        ticker = yf.Ticker(yahoo_symbol)

        # ----------------------------------------------------
        # FAST INFO
        # ----------------------------------------------------

        try:

            fast_info = ticker.fast_info

            price = fast_info.get(
                "last_price"
            )

            if price is not None:

                price = float(price)

                if price > 0:

                    print(
                        f"[MarketIQ] Live price: "
                        f"{yahoo_symbol} "
                        f"₹{price:.2f}"
                    )

                    return round(price, 2)

        except Exception as e:

            print(
                f"[MarketIQ] fast_info failed "
                f"for {yahoo_symbol}: {e}"
            )

        # ----------------------------------------------------
        # INTRADAY FALLBACK
        # ----------------------------------------------------

        try:

            df = ticker.history(
                period="1d",
                interval="5m",
                timeout=10,
            )

            if (
                df is not None
                and not df.empty
                and "Close" in df.columns
            ):

                closes = (
                    df["Close"]
                    .dropna()
                )

                if not closes.empty:

                    price = float(
                        closes.iloc[-1]
                    )

                    if price > 0:

                        print(
                            f"[MarketIQ] Fallback price: "
                            f"{yahoo_symbol} "
                            f"₹{price:.2f}"
                        )

                        return round(price, 2)

        except Exception as e:

            print(
                f"[MarketIQ] Intraday fallback "
                f"failed for "
                f"{yahoo_symbol}: {e}"
            )

        return None

    except Exception as e:

        print(
            f"[MarketIQ] Live price error "
            f"for {yahoo_symbol}: {e}"
        )

        return None


# ============================================================
# COMPLETE STOCK DATA
# ============================================================

def get_stock_data(symbol: str):

    yahoo_symbol = resolve_symbol(symbol)

    if not yahoo_symbol:

        return {
            "success": False,
            "symbol": None,
            "data": pd.DataFrame(),
            "price": None,
        }

    df = get_stock_history(
        yahoo_symbol
    )

    if df.empty:

        return {
            "success": False,
            "symbol": yahoo_symbol,
            "data": pd.DataFrame(),
            "price": None,
        }

    price = get_live_price(
        yahoo_symbol
    )

    # --------------------------------------------------------
    # Historical close fallback
    # --------------------------------------------------------

    if price is None:

        try:

            price = float(
                df["Close"]
                .dropna()
                .iloc[-1]
            )

        except Exception:

            price = None

    return {
        "success": True,
        "symbol": yahoo_symbol,
        "data": df,
        "price": (
            round(price, 2)
            if price is not None
            else None
        ),
    }