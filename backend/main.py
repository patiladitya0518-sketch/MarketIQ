from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from api.health import router as health_router
from api.stock import router as stock_router
from api.chart import router as chart_router

app = FastAPI(
    title="MarketIQ API",
    description="AI Stock Market Analysis API",
    version="1.2.0",
)

# ==========================================================
# CORS
# ==========================================================

origins = [
    "http://localhost:3000",
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