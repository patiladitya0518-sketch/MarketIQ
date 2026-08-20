from collections import defaultdict

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
# GET LIVE PORTFOLIO
# GROUP DUPLICATE STOCKS INTO ONE HOLDING
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

    # ========================================================
    # GROUP DATABASE ENTRIES BY SYMBOL
    # ========================================================

    grouped = defaultdict(
        lambda: {
            "ids": [],
            "quantity": 0,
            "total_invested": 0.0,
        }
    )

    for item in portfolio:

        symbol = item.symbol.upper()

        invested = (
            item.quantity * item.average_price
        )

        grouped[symbol]["ids"].append(item.id)

        grouped[symbol]["quantity"] += item.quantity

        grouped[symbol]["total_invested"] += invested

    holdings = []

    total_invested = 0.0
    total_current_value = 0.0

    profitable_holdings = 0
    losing_holdings = 0

    best_performer = None
    worst_performer = None

    allocation_total = 0.0

    # ========================================================
    # PROCESS EACH UNIQUE STOCK
    # ========================================================

    for symbol, data in grouped.items():

        quantity = data["quantity"]

        invested_value = data["total_invested"]

        # ----------------------------------------------------
        # WEIGHTED AVERAGE PRICE
        # ----------------------------------------------------

        if quantity > 0:
            average_price = (
                invested_value / quantity
            )
        else:
            average_price = 0.0

        total_invested += invested_value

        # ----------------------------------------------------
        # GET LIVE PRICE
        # ----------------------------------------------------

        current_price = get_live_price(symbol)

        # ----------------------------------------------------
        # PRICE UNAVAILABLE
        # ----------------------------------------------------

        if current_price is None:

            holdings.append({
                "id": data["ids"][0],
                "symbol": symbol,
                "quantity": quantity,

                "average_price": round(
                    average_price,
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

                "allocation_percentage": 0.0,

                "price_available": False,
            })

            continue

        # ----------------------------------------------------
        # CALCULATE P&L
        # ----------------------------------------------------

        pnl_data = calculate_holding_pnl(
            quantity=quantity,
            average_price=average_price,
            current_price=current_price,
        )

        current_value = pnl_data[
            "current_value"
        ]

        pnl = pnl_data["pnl"]

        pnl_percentage = pnl_data[
            "pnl_percentage"
        ]

        total_current_value += current_value

        allocation_total += current_value

        # ----------------------------------------------------
        # PROFIT / LOSS COUNT
        # ----------------------------------------------------

        if pnl > 0:

            profitable_holdings += 1

        elif pnl < 0:

            losing_holdings += 1

        # ----------------------------------------------------
        # BEST PERFORMER
        # ----------------------------------------------------

        if (
            best_performer is None
            or pnl_percentage
            > best_performer["pnl_percentage"]
        ):

            best_performer = {
                "symbol": symbol,

                "pnl": round(
                    pnl,
                    2,
                ),

                "pnl_percentage": round(
                    pnl_percentage,
                    2,
                ),
            }

        # ----------------------------------------------------
        # WORST PERFORMER
        # ----------------------------------------------------

        if (
            worst_performer is None
            or pnl_percentage
            < worst_performer["pnl_percentage"]
        ):

            worst_performer = {
                "symbol": symbol,

                "pnl": round(
                    pnl,
                    2,
                ),

                "pnl_percentage": round(
                    pnl_percentage,
                    2,
                ),
            }

        # ----------------------------------------------------
        # ADD HOLDING
        # ----------------------------------------------------

        holdings.append({
            "id": data["ids"][0],

            "symbol": symbol,

            "quantity": quantity,

            "average_price": round(
                average_price,
                2,
            ),

            "current_price": round(
                current_price,
                2,
            ),

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

            "allocation_percentage": 0.0,

            "price_available": True,
        })

    # ========================================================
    # TOTAL PORTFOLIO P&L
    # ========================================================

    total_pnl = (
        total_current_value
        - total_invested
    )

    if total_invested > 0:

        total_pnl_percentage = (
            total_pnl
            / total_invested
        ) * 100

    else:

        total_pnl_percentage = 0.0

    # ========================================================
    # PORTFOLIO ALLOCATION
    # ========================================================

    if allocation_total > 0:

        for holding in holdings:

            if holding["current_value"] is not None:

                holding[
                    "allocation_percentage"
                ] = round(
                    (
                        holding["current_value"]
                        / allocation_total
                    ) * 100,
                    2,
                )

    # ========================================================
    # PORTFOLIO HEALTH
    # ========================================================

    total_holdings = len(holdings)

    if total_holdings == 0:

        portfolio_health = "No Holdings"
        risk_level = "No Data"

    else:

        profit_ratio = (
            profitable_holdings
            / total_holdings
        ) * 100

        largest_allocation = 0.0

        for holding in holdings:

            allocation = holding[
                "allocation_percentage"
            ]

            if allocation > largest_allocation:

                largest_allocation = allocation

        if largest_allocation >= 70:

            portfolio_health = (
                "High Concentration"
            )

            risk_level = "High"

        elif largest_allocation >= 50:

            portfolio_health = (
                "Moderate Concentration"
            )

            risk_level = "Medium"

        elif profit_ratio >= 60:

            portfolio_health = "Healthy"

            risk_level = "Low"

        elif profit_ratio >= 40:

            portfolio_health = "Balanced"

            risk_level = "Medium"

        else:

            portfolio_health = (
                "Under Pressure"
            )

            risk_level = "High"

    # ========================================================
    # RESPONSE
    # ========================================================

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

            "total_holdings": total_holdings,

            "profitable_holdings":
                profitable_holdings,

            "losing_holdings":
                losing_holdings,

            "best_performer":
                best_performer,

            "worst_performer":
                worst_performer,

            "portfolio_health":
                portfolio_health,

            "risk_level":
                risk_level,
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