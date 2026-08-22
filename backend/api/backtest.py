from fastapi import APIRouter, Query

from services.backtest_service import run_backtest


router = APIRouter(
    prefix="/backtest",
    tags=["Backtesting"],
)


@router.get("/{symbol}")
def backtest(
    symbol: str,
    period: str = Query(
        "1y",
        description="Historical period"
    ),
):
    return run_backtest(
        symbol,
        period,
    )