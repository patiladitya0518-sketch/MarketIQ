from services.data_service import get_stock_history


def get_live_price(symbol: str):
    """
    Get the latest available NSE price for a stock.
    """

    df = get_stock_history(symbol)

    if df.empty:
        return None

    latest_price = float(
        df.iloc[-1]["Close"]
    )

    return round(
        latest_price,
        2,
    )


def calculate_holding_pnl(
    quantity: int,
    average_price: float,
    current_price: float,
):
    invested_value = (
        quantity * average_price
    )

    current_value = (
        quantity * current_price
    )

    pnl = (
        current_value - invested_value
    )

    if invested_value > 0:
        pnl_percentage = (
            pnl / invested_value
        ) * 100
    else:
        pnl_percentage = 0.0

    return {
        "invested_value": round(
            invested_value,
            2,
        ),

        "current_value": round(
            current_value,
            2,
        ),

        "pnl": round(
            pnl,
            2,
        ),

        "pnl_percentage": round(
            pnl_percentage,
            2,
        ),
    }