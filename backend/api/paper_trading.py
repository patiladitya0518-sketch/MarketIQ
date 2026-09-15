from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies.auth import (
    get_current_user,
    get_db,
)

from schemas.paper_trading import (
    PaperAccountResponse,
    PaperOrderRequest,
    PaperOrderResponse,
)

from services.paper_trading_service import (
    execute_order,
    get_account_summary,
    reset_account,
)


router = APIRouter(
    prefix="/paper-trading",
    tags=["Paper Trading"],
)


# ============================================================
# GET PAPER TRADING ACCOUNT
# ============================================================

@router.get(
    "/account",
    response_model=PaperAccountResponse,
)
def get_paper_account(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated user's paper
    trading account, positions and recent trades.
    """

    return get_account_summary(
        db,
        str(current_user.id),
    )


# ============================================================
# PLACE PAPER ORDER
# ============================================================

@router.post(
    "/order",
    response_model=PaperOrderResponse,
)
def place_paper_order(
    order: PaperOrderRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Execute a virtual BUY or SELL order.

    If price is not supplied, MarketIQ uses
    the latest available market price.
    """

    try:

        trade = execute_order(
            db=db,
            user_id=str(current_user.id),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=order.price,
        )

        account = get_account_summary(
            db,
            str(current_user.id),
        )

        trade_response = {
            "id": trade.id,
            "symbol": trade.symbol,
            "side": trade.side,
            "quantity": trade.quantity,
            "price": float(trade.price),
            "total_value": float(
                trade.total_value
            ),
            "realized_pnl": float(
                trade.realized_pnl
            ),
            "status": trade.status,
            "notes": trade.notes,
            "executed_at": trade.executed_at,
        }

        return {
            "success": True,
            "message": (
                f"{trade.side} order executed "
                f"successfully for "
                f"{trade.quantity} "
                f"{trade.symbol}."
            ),
            "trade": trade_response,
            "account": account,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        db.rollback()

        print(
            "[Paper Trading] Order failed:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to execute paper "
                "trading order."
            ),
        )


# ============================================================
# RESET PAPER ACCOUNT
# ============================================================

@router.post(
    "/reset",
    response_model=PaperAccountResponse,
)
def reset_paper_account(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reset the authenticated user's paper
    trading account to ₹1,00,000.
    """

    try:

        return reset_account(
            db,
            str(current_user.id),
        )

    except Exception as error:

        db.rollback()

        print(
            "[Paper Trading] Reset failed:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to reset paper "
                "trading account."
            ),
        )