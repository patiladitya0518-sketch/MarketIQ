from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Config
from config import settings

# Routers
from api.health import router as health_router
from api.stock import router as stock_router
from api.chart import router as chart_router
from api.auth import router as auth_router
from api.portfolio import router as portfolio_router
from api.backtest import router as backtest_router  # NEW


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Stock Market Analysis API",
    version=settings.APP_VERSION,
)


# ==========================================================
# CORS
# ==========================================================

origins = [
    settings.FRONTEND_URL,
    "http://127.0.0.1:3000",
    "https://market-iq-five-orpin.vercel.app",
]


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
app.include_router(backtest_router)  # NEW