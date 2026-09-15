from fastapi import APIRouter, Query

from services.backtest_service import (
    run_backtest,
    run_walk_forward_oos,
)


router = APIRouter(
    prefix="/backtest",
    tags=["Backtest"],
)


@router.get("/walk-forward/{symbol}")
def walk_forward_backtest(
    symbol: str,
    period: str = Query(
        default="5y",
        pattern="^(6mo|1y|2y|5y)$",
    ),
    test_start_date: str | None = Query(
        default=None,
        description="Optional OOS start date in YYYY-MM-DD format.",
    ),
    test_end_date: str | None = Query(
        default=None,
        description="Optional OOS end date in YYYY-MM-DD format.",
    ),
    oos_ratio: float = Query(
        default=0.40,
        ge=0.20,
        le=0.60,
        description="OOS fraction used when test_start_date is not supplied.",
    ),
):
    return run_walk_forward_oos(
        symbol=symbol,
        period=period,
        test_start_date=test_start_date,
        test_end_date=test_end_date,
        oos_ratio=oos_ratio,
    )


@router.get("/{symbol}")
def backtest(
    symbol: str,
    period: str = Query(
        default="1y",
        pattern="^(6mo|1y|2y|5y)$",
    ),
):
    return run_backtest(
        symbol=symbol,
        period=period,
    )
