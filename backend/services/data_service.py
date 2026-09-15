import math
import time
from functools import lru_cache

import pandas as pd
import yfinance as yf


# ============================================================
# PRODUCTION DATA SETTINGS
# ============================================================

YAHOO_TIMEOUT_SECONDS = 10
YAHOO_RETRIES = 2
YAHOO_RETRY_DELAY_SECONDS = 1.0


def _log(message: str):
    """Render-friendly diagnostic logging."""
    print(f"[MarketIQ] {message}", flush=True)


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
            timeout=YAHOO_TIMEOUT_SECONDS,
        )

        return (
            history is not None
            and not history.empty
        )

    except Exception as e:

        _log(
            f"Symbol check failed for {yahoo_symbol}: {e!r}"
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

        _log(
            f"Mapping resolved: {query} -> {symbol}"
        )

        return symbol

    # --------------------------------------------------------
    # Yahoo search
    # --------------------------------------------------------

    try:

        _log(
            f"Automatic company search: {query}"
        )

        search = yf.Search(
            query,
            max_results=20,
            news_count=0,
            enable_fuzzy_query=True,
        )

        quotes = search.quotes or []

        if not quotes:

            _log(
                f"No Yahoo results for: {query}"
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

            _log(
                f"No Indian equity found for: {query}"
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

                _log(
                    f"NSE search resolved: {query} -> {yahoo_symbol}"
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

                _log(
                    f"BSE search resolved: {query} -> {yahoo_symbol}"
                )

                return yahoo_symbol

        return None

    except Exception as e:

        _log(
            f"Yahoo search failed for '{query}': {e!r}"
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
    # STEP 1 — TRUST EXPLICIT NSE/BSE MAPPING
    #
    # For manually mapped Indian stocks we already know the
    # intended Yahoo symbol. Do NOT perform a preliminary
    # Yahoo history request here because that request can fail
    # independently of the actual historical-data download
    # (for example due to temporary Yahoo/network restrictions).
    # The real data availability check is performed by
    # get_stock_history().
    # --------------------------------------------------------

    if query in COMPANY_SYMBOLS:

        yahoo_symbol = COMPANY_SYMBOLS[query]

        _log(
            f"Mapping resolved: {query} -> {yahoo_symbol}"
        )

        return yahoo_symbol

    # --------------------------------------------------------
    # STEP 2 — Explicit Yahoo NSE/BSE symbol
    # --------------------------------------------------------

    if query.endswith(".NS") or query.endswith(".BO"):

        _log(
            f"Explicit Yahoo symbol resolved: {query}"
        )

        return query

    # --------------------------------------------------------
    # STEP 3 — Unknown ticker: verify NSE/BSE candidates
    # --------------------------------------------------------

    candidates = get_candidate_symbols(query)

    for yahoo_symbol in candidates:

        if check_symbol(yahoo_symbol):

            _log(
                f"Direct symbol resolved: {query} -> {yahoo_symbol}"
            )

            return yahoo_symbol

    # --------------------------------------------------------
    # STEP 4 — Yahoo company search
    # --------------------------------------------------------

    searched_symbol = search_stock_symbol(query)

    if searched_symbol:

        if check_symbol(searched_symbol):

            _log(
                f"Search symbol verified: {query} -> {searched_symbol}"
            )

            return searched_symbol

    # --------------------------------------------------------
    # STEP 5 — Not found
    # --------------------------------------------------------

    _log(
        f"Could not resolve stock: {query}"
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

        _log(
            f"Unable to resolve: {symbol}"
        )

        return pd.DataFrame()

    last_error = None

    for attempt in range(1, YAHOO_RETRIES + 1):

        try:

            _log(
                f"Fetching history: {yahoo_symbol} "
                f"(attempt {attempt}/{YAHOO_RETRIES})"
            )

            df = yf.download(
                yahoo_symbol,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=False,
                timeout=YAHOO_TIMEOUT_SECONDS,
                threads=False,
            )

            if df is None or df.empty:

                _log(
                    f"No historical data for {yahoo_symbol} "
                    f"on attempt {attempt}"
                )

                if attempt < YAHOO_RETRIES:
                    time.sleep(YAHOO_RETRY_DELAY_SECONDS)
                    continue

                return pd.DataFrame()

            # ------------------------------------------------
            # Fix MultiIndex
            # ------------------------------------------------

            if isinstance(
                df.columns,
                pd.MultiIndex,
            ):

                df.columns = (
                    df.columns
                    .get_level_values(0)
                )

            # ------------------------------------------------
            # Remove duplicates
            # ------------------------------------------------

            df = df.loc[
                :,
                ~df.columns.duplicated()
            ]

            # ------------------------------------------------
            # Required columns
            # ------------------------------------------------

            required_columns = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                _log(
                    f"Missing columns for {yahoo_symbol}: "
                    f"{', '.join(missing_columns)}"
                )

                return pd.DataFrame()

            # ------------------------------------------------
            # Clean
            # ------------------------------------------------

            df = df.dropna(
                subset=["Close"]
            )

            if df.empty:
                return pd.DataFrame()

            _log(
                f"History loaded: {yahoo_symbol} "
                f"({len(df)} candles)"
            )

            return df

        except Exception as e:

            last_error = e

            _log(
                f"Historical data error for {yahoo_symbol} "
                f"on attempt {attempt}/{YAHOO_RETRIES}: {e!r}"
            )

            if attempt < YAHOO_RETRIES:
                time.sleep(YAHOO_RETRY_DELAY_SECONDS)

    _log(
        f"Historical data unavailable for {yahoo_symbol}: "
        f"{last_error!r}"
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

        _log(
            f"Fetching live price: {yahoo_symbol}"
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

                if math.isfinite(price) and price > 0:

                    _log(
                        f"Live price: {yahoo_symbol} ₹{price:.2f}"
                    )

                    return round(price, 2)

        except Exception as e:

            _log(
                f"fast_info failed for {yahoo_symbol}: {e!r}"
            )

        # ----------------------------------------------------
        # INTRADAY FALLBACK
        # ----------------------------------------------------

        for attempt in range(1, YAHOO_RETRIES + 1):

            try:

                _log(
                    f"Fetching intraday fallback: {yahoo_symbol} "
                    f"(attempt {attempt}/{YAHOO_RETRIES})"
                )

                df = ticker.history(
                    period="1d",
                    interval="5m",
                    timeout=YAHOO_TIMEOUT_SECONDS,
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

                        if math.isfinite(price) and price > 0:

                            _log(
                                f"Fallback price: {yahoo_symbol} "
                                f"₹{price:.2f}"
                            )

                            return round(price, 2)

                if attempt < YAHOO_RETRIES:
                    time.sleep(YAHOO_RETRY_DELAY_SECONDS)

            except Exception as e:

                _log(
                    f"Intraday fallback failed for {yahoo_symbol} "
                    f"on attempt {attempt}/{YAHOO_RETRIES}: {e!r}"
                )

                if attempt < YAHOO_RETRIES:
                    time.sleep(YAHOO_RETRY_DELAY_SECONDS)

        return None

    except Exception as e:

        _log(
            f"Live price error for {yahoo_symbol}: {e!r}"
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

            if not math.isfinite(price) or price <= 0:
                price = None

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
