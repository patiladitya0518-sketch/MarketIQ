from decimal import Decimal
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.paper_trading import (
    PaperTrade,
    PaperTradingAccount,
    PaperTradingPosition,
)

from services.data_service import get_stock_history


INITIAL_CAPITAL = Decimal("100000.00")


# ============================================================
# HELPERS
# ============================================================

def money(value) -> Decimal:
    return Decimal(str(value or 0))


def resolve_market_price(symbol: str) -> Decimal:
    """
    Get the latest available market close price
    from the existing MarketIQ data service.
    """

    df = get_stock_history(
        symbol,
        period="5d",
        interval="1d",
    )

    if df is None or df.empty:
        raise ValueError(
            f"Unable to retrieve market price for {symbol}."
        )

    try:
        latest_price = df["Close"].iloc[-1]
    except Exception:
        raise ValueError(
            f"Market price is unavailable for {symbol}."
        )

    price = money(latest_price)

    if price <= 0:
        raise ValueError(
            f"Invalid market price for {symbol}."
        )

    return price


# ============================================================
# GET OR CREATE ACCOUNT
# ============================================================

def get_or_create_account(
    db: Session,
    user_id: str,
) -> PaperTradingAccount:

    account = (
        db.query(PaperTradingAccount)
        .filter(
            PaperTradingAccount.user_id == str(user_id)
        )
        .first()
    )

    if account:
        return account

    account = PaperTradingAccount(
        user_id=str(user_id),
        initial_capital=INITIAL_CAPITAL,
        available_cash=INITIAL_CAPITAL,
        realized_pnl=Decimal("0.00"),
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


# ============================================================
# GET POSITION
# ============================================================

def get_position(
    db: Session,
    user_id: str,
    symbol: str,
) -> Optional[PaperTradingPosition]:

    return (
        db.query(PaperTradingPosition)
        .filter(
            PaperTradingPosition.user_id == str(user_id),
            PaperTradingPosition.symbol == symbol,
        )
        .first()
    )


# ============================================================
# EXECUTE BUY
# ============================================================

def execute_buy(
    db: Session,
    account: PaperTradingAccount,
    user_id: str,
    symbol: str,
    quantity: int,
    price: Decimal,
) -> PaperTrade:

    total_value = price * quantity

    available_cash = money(
        account.available_cash
    )

    if total_value > available_cash:
        raise ValueError(
            "Insufficient virtual cash for this BUY order."
        )

    position = get_position(
        db,
        user_id,
        symbol,
    )

    if position:

        old_quantity = position.quantity

        old_average = money(
            position.average_price
        )

        new_quantity = (
            old_quantity + quantity
        )

        total_cost = (
            old_average * old_quantity
        ) + total_value

        new_average = (
            total_cost / new_quantity
        )

        position.quantity = new_quantity
        position.average_price = new_average

    else:

        position = PaperTradingPosition(
            user_id=str(user_id),
            symbol=symbol,
            quantity=quantity,
            average_price=price,
        )

        db.add(position)

    account.available_cash = (
        available_cash - total_value
    )

    trade = PaperTrade(
        user_id=str(user_id),
        symbol=symbol,
        side="BUY",
        quantity=quantity,
        price=price,
        total_value=total_value,
        realized_pnl=Decimal("0.00"),
        status="EXECUTED",
        notes="Paper trading BUY order",
    )

    db.add(trade)

    return trade


# ============================================================
# EXECUTE SELL
# ============================================================

def execute_sell(
    db: Session,
    account: PaperTradingAccount,
    user_id: str,
    symbol: str,
    quantity: int,
    price: Decimal,
) -> PaperTrade:

    position = get_position(
        db,
        user_id,
        symbol,
    )

    if not position or position.quantity <= 0:
        raise ValueError(
            f"No open paper position exists for {symbol}."
        )

    if quantity > position.quantity:
        raise ValueError(
            f"Cannot sell {quantity} shares. "
            f"Current paper position is only "
            f"{position.quantity} shares."
        )

    average_price = money(
        position.average_price
    )

    total_value = price * quantity

    realized_pnl = (
        price - average_price
    ) * quantity

    account.available_cash = (
        money(account.available_cash)
        + total_value
    )

    account.realized_pnl = (
        money(account.realized_pnl)
        + realized_pnl
    )

    position.quantity -= quantity

    if position.quantity == 0:
        db.delete(position)

    trade = PaperTrade(
        user_id=str(user_id),
        symbol=symbol,
        side="SELL",
        quantity=quantity,
        price=price,
        total_value=total_value,
        realized_pnl=realized_pnl,
        status="EXECUTED",
        notes="Paper trading SELL order",
    )

    db.add(trade)

    return trade


# ============================================================
# EXECUTE ORDER
# ============================================================

def execute_order(
    db: Session,
    user_id: str,
    symbol: str,
    side: str,
    quantity: int,
    price: Optional[float] = None,
) -> PaperTrade:

    symbol = (
        symbol.strip()
        .upper()
    )

    side = (
        side.strip()
        .upper()
    )

    if not symbol:
        raise ValueError(
            "Stock symbol is required."
        )

    if side not in ("BUY", "SELL"):
        raise ValueError(
            "Order side must be BUY or SELL."
        )

    if quantity <= 0:
        raise ValueError(
            "Quantity must be greater than zero."
        )

    account = get_or_create_account(
        db,
        user_id,
    )

    if price is None:
        execution_price = resolve_market_price(
            symbol
        )
    else:
        execution_price = money(price)

    if execution_price <= 0:
        raise ValueError(
            "Order price must be greater than zero."
        )

    if side == "BUY":

        trade = execute_buy(
            db=db,
            account=account,
            user_id=str(user_id),
            symbol=symbol,
            quantity=quantity,
            price=execution_price,
        )

    else:

        trade = execute_sell(
            db=db,
            account=account,
            user_id=str(user_id),
            symbol=symbol,
            quantity=quantity,
            price=execution_price,
        )

    account.updated_at = (
        __import__("datetime")
        .datetime.now(
            __import__("datetime").timezone.utc
        )
    )

    db.commit()
    db.refresh(trade)

    return trade


# ============================================================
# BUILD POSITION RESPONSE DATA
# ============================================================

def build_position_data(
    db: Session,
    user_id: str,
):

    positions = (
        db.query(PaperTradingPosition)
        .filter(
            PaperTradingPosition.user_id
            == str(user_id)
        )
        .order_by(
            PaperTradingPosition.symbol.asc()
        )
        .all()
    )

    result = []

    for position in positions:

        try:
            current_price = (
                resolve_market_price(
                    position.symbol
                )
            )
        except Exception:
            current_price = money(
                position.average_price
            )

        quantity = position.quantity

        average_price = money(
            position.average_price
        )

        invested_value = (
            average_price * quantity
        )

        current_value = (
            current_price * quantity
        )

        unrealized_pnl = (
            current_value
            - invested_value
        )

        if invested_value > 0:
            unrealized_percentage = (
                unrealized_pnl
                / invested_value
            ) * Decimal("100")
        else:
            unrealized_percentage = (
                Decimal("0")
            )

        result.append(
            {
                "symbol": position.symbol,
                "quantity": quantity,
                "average_price": float(
                    average_price
                ),
                "current_price": float(
                    current_price
                ),
                "invested_value": float(
                    invested_value
                ),
                "current_value": float(
                    current_value
                ),
                "unrealized_pnl": float(
                    unrealized_pnl
                ),
                "unrealized_pnl_percentage": float(
                    unrealized_percentage
                ),
            }
        )

    return result


# ============================================================
# BUILD ACCOUNT SUMMARY
# ============================================================

def get_account_summary(
    db: Session,
    user_id: str,
):

    account = get_or_create_account(
        db,
        user_id,
    )

    positions = build_position_data(
        db,
        user_id,
    )

    invested_value = sum(
        Decimal(
            str(
                item["invested_value"]
            )
        )
        for item in positions
    )

    current_value = sum(
        Decimal(
            str(
                item["current_value"]
            )
        )
        for item in positions
    )

    unrealized_pnl = (
        current_value
        - invested_value
    )

    available_cash = money(
        account.available_cash
    )

    total_equity = (
        available_cash
        + current_value
    )

    realized_pnl = money(
        account.realized_pnl
    )

    total_pnl = (
        realized_pnl
        + unrealized_pnl
    )

    initial_capital = money(
        account.initial_capital
    )

    if initial_capital > 0:
        total_pnl_percentage = (
            total_pnl
            / initial_capital
        ) * Decimal("100")
    else:
        total_pnl_percentage = Decimal("0")

    trades = (
        db.query(PaperTrade)
        .filter(
            PaperTrade.user_id
            == str(user_id)
        )
        .order_by(
            desc(PaperTrade.executed_at)
        )
        .limit(20)
        .all()
    )

    recent_trades = [
        {
            "id": trade.id,
            "symbol": trade.symbol,
            "side": trade.side,
            "quantity": trade.quantity,
            "price": float(
                money(trade.price)
            ),
            "total_value": float(
                money(trade.total_value)
            ),
            "realized_pnl": float(
                money(trade.realized_pnl)
            ),
            "status": trade.status,
            "notes": trade.notes,
            "executed_at": trade.executed_at,
        }
        for trade in trades
    ]

    return {
        "initial_capital": float(
            initial_capital
        ),
        "available_cash": float(
            available_cash
        ),
        "invested_value": float(
            invested_value
        ),
        "current_value": float(
            current_value
        ),
        "total_equity": float(
            total_equity
        ),
        "realized_pnl": float(
            realized_pnl
        ),
        "unrealized_pnl": float(
            unrealized_pnl
        ),
        "total_pnl": float(
            total_pnl
        ),
        "total_pnl_percentage": float(
            total_pnl_percentage
        ),
        "positions": positions,
        "recent_trades": recent_trades,
    }


# ============================================================
# RESET ACCOUNT
# ============================================================

def reset_account(
    db: Session,
    user_id: str,
):

    account = get_or_create_account(
        db,
        user_id,
    )

    db.query(PaperTrade).filter(
        PaperTrade.user_id
        == str(user_id)
    ).delete(
        synchronize_session=False
    )

    db.query(PaperTradingPosition).filter(
        PaperTradingPosition.user_id
        == str(user_id)
    ).delete(
        synchronize_session=False
    )

    account.available_cash = (
        INITIAL_CAPITAL
    )

    account.realized_pnl = (
        Decimal("0.00")
    )

    account.updated_at = (
        __import__("datetime")
        .datetime.now(
            __import__("datetime").timezone.utc
        )
    )

    db.commit()

    return get_account_summary(
        db,
        user_id,
    )