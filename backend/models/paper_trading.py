from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)

from database.base import Base


# ============================================================
# PAPER TRADING ACCOUNT
# ============================================================

class PaperTradingAccount(Base):
    __tablename__ = "paper_trading_accounts"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    initial_capital = Column(
        Numeric(18, 2),
        nullable=False,
        default=100000.00,
    )

    available_cash = Column(
        Numeric(18, 2),
        nullable=False,
        default=100000.00,
    )

    realized_pnl = Column(
        Numeric(18, 2),
        nullable=False,
        default=0.00,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ============================================================
# PAPER TRADING POSITION
# ============================================================

class PaperTradingPosition(Base):
    __tablename__ = "paper_trading_positions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    symbol = Column(
        String(50),
        nullable=False,
        index=True,
    )

    quantity = Column(
        Integer,
        nullable=False,
        default=0,
    )

    average_price = Column(
        Numeric(18, 4),
        nullable=False,
        default=0.00,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "symbol",
            name="uq_paper_position_user_symbol",
        ),
    )


# ============================================================
# PAPER TRADE HISTORY
# ============================================================

class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    symbol = Column(
        String(50),
        nullable=False,
        index=True,
    )

    side = Column(
        String(10),
        nullable=False,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    price = Column(
        Numeric(18, 4),
        nullable=False,
    )

    total_value = Column(
        Numeric(18, 2),
        nullable=False,
    )

    realized_pnl = Column(
        Numeric(18, 2),
        nullable=False,
        default=0.00,
    )

    status = Column(
        String(20),
        nullable=False,
        default="EXECUTED",
    )

    notes = Column(
        Text,
        nullable=True,
    )

    executed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )