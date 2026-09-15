from pydantic import BaseModel, Field


class PortfolioCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    quantity: int = Field(..., gt=0)
    average_price: float = Field(..., gt=0)


class PortfolioResponse(BaseModel):
    id: str
    symbol: str
    quantity: int
    average_price: float

    class Config:
        from_attributes = True