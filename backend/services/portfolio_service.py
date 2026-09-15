from sqlalchemy.orm import Session

from models.portfolio import Portfolio
from schemas.portfolio import PortfolioCreate


def add_to_portfolio(
    db: Session,
    user_id: str,
    portfolio_data: PortfolioCreate,
):
    portfolio = Portfolio(
        user_id=user_id,
        symbol=portfolio_data.symbol.upper(),
        quantity=portfolio_data.quantity,
        average_price=portfolio_data.average_price,
    )

    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    return portfolio


def get_user_portfolio(
    db: Session,
    user_id: str,
):
    return (
        db.query(Portfolio)
        .filter(Portfolio.user_id == user_id)
        .all()
    )


def delete_from_portfolio(
    db: Session,
    user_id: str,
    portfolio_id: str,
):
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
        )
        .first()
    )

    if portfolio is None:
        return False

    db.delete(portfolio)
    db.commit()

    return True