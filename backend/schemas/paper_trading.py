from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================
# ORDER REQUEST
# ============================================================

class PaperOrderRequest(BaseModel):

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    side: str = Field(
        ...,
        description="BUY or SELL",
    )

    quantity: int = Field(
        ...,
        gt=0,
    )

    price: float | None = Field(
        default=None,
        gt=0,
    )


# ============================================================
# POSITION RESPONSE
# ============================================================

class PaperPositionResponse(BaseModel):

    symbol: str

    quantity: int

    average_price: float

    current_price: float

    invested_value: float

    current_value: float

    unrealized_pnl: float

    unrealized_pnl_percentage: float


# ============================================================
# TRADE RESPONSE
# ============================================================

class PaperTradeResponse(BaseModel):

    id: str

    symbol: str

    side: str

    quantity: int

    price: float

    total_value: float

    realized_pnl: float

    status: str

    notes: str | None = None

    executed_at: datetime


# ============================================================
# ACCOUNT RESPONSE
# ============================================================

class PaperAccountResponse(BaseModel):

    initial_capital: float

    available_cash: float

    invested_value: float

    current_value: float

    total_equity: float

    realized_pnl: float

    unrealized_pnl: float

    total_pnl: float

    total_pnl_percentage: float

    positions: list[PaperPositionResponse]

    recent_trades: list[PaperTradeResponse]


# ============================================================
# ORDER RESPONSE
# ============================================================

class PaperOrderResponse(BaseModel):

    success: bool

    message: str

    trade: PaperTradeResponse

    account: PaperAccountResponse