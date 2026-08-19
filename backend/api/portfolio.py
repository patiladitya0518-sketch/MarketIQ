from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies.auth import get_db, get_current_user

from schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
)

from services.portfolio_service import (
    add_to_portfolio,
    get_user_portfolio,
    delete_from_portfolio,
)

from services.portfolio_market_service import (
    get_live_price,
    calculate_holding_pnl,
)


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


# ============================================================
# ADD STOCK TO PORTFOLIO
# ============================================================

@router.post(
    "",
    response_model=PortfolioResponse,
)
def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return add_to_portfolio(
        db,
        current_user.id,
        portfolio_data,
    )


# ============================================================
# GET NORMAL PORTFOLIO
# ============================================================

@router.get(
    "",
    response_model=list[PortfolioResponse],
)
def get_portfolio(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_user_portfolio(
        db,
        current_user.id,
    )


# ============================================================
# GET LIVE PORTFOLIO WITH PRICE + P&L
# ============================================================

@router.get("/live")
def get_live_portfolio(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    portfolio = get_user_portfolio(
        db,
        current_user.id,
    )

    holdings = []

    total_invested = 0.0
    total_current_value = 0.0

    for item in portfolio:

        # Get latest market price
        current_price = get_live_price(item.symbol)

        # ----------------------------------------------------
        # Price unavailable
        # ----------------------------------------------------

        if current_price is None:

            invested_value = (
                item.quantity * item.average_price
            )

            total_invested += invested_value

            holdings.append({
                "id": item.id,
                "symbol": item.symbol,
                "quantity": item.quantity,
                "average_price": round(
                    item.average_price,
                    2,
                ),
                "current_price": None,
                "invested_value": round(
                    invested_value,
                    2,
                ),
                "current_value": None,
                "pnl": None,
                "pnl_percentage": None,
                "price_available": False,
            })

            continue

        # ----------------------------------------------------
        # Calculate P&L
        # ----------------------------------------------------

        pnl_data = calculate_holding_pnl(
            quantity=item.quantity,
            average_price=item.average_price,
            current_price=current_price,
        )

        total_invested += pnl_data["invested_value"]

        total_current_value += pnl_data["current_value"]

        holdings.append({
            "id": item.id,
            "symbol": item.symbol,
            "quantity": item.quantity,
            "average_price": round(
                item.average_price,
                2,
            ),
            "current_price": current_price,

            "invested_value": pnl_data[
                "invested_value"
            ],

            "current_value": pnl_data[
                "current_value"
            ],

            "pnl": pnl_data[
                "pnl"
            ],

            "pnl_percentage": pnl_data[
                "pnl_percentage"
            ],

            "price_available": True,
        })

    # ========================================================
    # TOTAL PORTFOLIO P&L
    # ========================================================

    total_pnl = (
        total_current_value - total_invested
    )

    if total_invested > 0:
        total_pnl_percentage = (
            total_pnl / total_invested
        ) * 100
    else:
        total_pnl_percentage = 0.0

    return {
        "success": True,

        "holdings": holdings,

        "summary": {
            "total_invested": round(
                total_invested,
                2,
            ),

            "total_current_value": round(
                total_current_value,
                2,
            ),

            "total_pnl": round(
                total_pnl,
                2,
            ),

            "total_pnl_percentage": round(
                total_pnl_percentage,
                2,
            ),
        },
    }


# ============================================================
# DELETE STOCK FROM PORTFOLIO
# ============================================================

@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted = delete_from_portfolio(
        db,
        current_user.id,
        portfolio_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Portfolio item not found",
        )

    return {
        "success": True,
        "message": "Portfolio item deleted successfully",
    }