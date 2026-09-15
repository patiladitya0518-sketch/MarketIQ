from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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

    # Existing production frontend compatibility
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
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ==========================================================
# PRODUCTION SECURITY / RESPONSE MIDDLEWARE
# ==========================================================

@app.middleware("http")
async def production_response_middleware(
    request: Request,
    call_next,
):
    """Add lightweight production headers without changing API logic."""

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "0"

    return response


# ==========================================================
# CLEAN API ERROR HANDLERS
# ==========================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    """Return consistent JSON for expected HTTP errors."""

    detail = exc.detail

    if isinstance(detail, str):
        message = detail
    else:
        message = "Request could not be completed."

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "HTTP_ERROR",
                "message": message,
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Return a clean 422 response for invalid request parameters."""

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "type": "VALIDATION_ERROR",
                "message": "Invalid request parameters.",
                "fields": [
                    {
                        "field": " -> ".join(
                            str(part)
                            for part in error.get("loc", [])
                        ),
                        "message": str(error.get("msg", "Invalid value")),
                    }
                    for error in exc.errors()
                ],
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    """Hide internal exception details from clients in production."""

    print(
        f"[MarketIQ] Unhandled API error "
        f"{request.method} {request.url.path}: {exc!r}",
        flush=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again.",
            },
        },
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
