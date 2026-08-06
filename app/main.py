from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import categories, products, stock_movements


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Stockroom API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(stock_movements.router, prefix="/api/v1/stock-movements", tags=["stock-movements"])


@app.get("/health")
async def health():
    return {"status": "ok"}
