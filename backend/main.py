from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ==========================================================
# CONFIG
# ==========================================================

from config import settings

# ==========================================================
# ROUTERS
# ==========================================================

from api.health import router as health_router
from api.stock import router as stock_router
from api.chart import router as chart_router
from api.auth import router as auth_router
from api.portfolio import router as portfolio_router
from api.backtest import router as backtest_router
from api.paper_trading import router as paper_trading_router


# ==========================================================
# APPLICATION
# ==========================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Stock Market Analysis API",
    version=settings.APP_VERSION,
)


# ==========================================================
# CORS
# ==========================================================

origins = [
    # Local development
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    # Local network development
    "http://192.168.1.6:3000",

    # Configured frontend URL
    settings.FRONTEND_URL,

    # Production frontend
    "https://market-iq-five-orpin.vercel.app",
]


# Remove empty values and duplicates
origins = list(
    dict.fromkeys(
        origin
        for origin in origins
        if origin
    )
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# REGISTER ROUTERS
# ==========================================================

app.include_router(health_router)
app.include_router(stock_router)
app.include_router(chart_router)
app.include_router(auth_router)
app.include_router(portfolio_router)
app.include_router(backtest_router)
app.include_router(paper_trading_router)