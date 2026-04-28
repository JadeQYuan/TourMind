from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.suppliers import router as suppliers_router
from app.routers.accounts import router as accounts_router
from app.routers.itineraries import router as itineraries_router, public_router as itineraries_public_router
from app.routers.contracts import router as contracts_router, public_router as contracts_public_router
from app.routers.bills import router as bills_router
from app.routers.files import router as files_router
from app.routers.products import router as products_router
from app.routers.orders import router as orders_router
from app.routers.audit import router as audit_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title="TourMind API",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

for r in [
    auth_router,
    users_router,
    suppliers_router,
    accounts_router,
    products_router,
    itineraries_router,
    contracts_router,
    bills_router,
    files_router,
    orders_router,
    audit_router,
    dashboard_router,
]:    app.include_router(r, prefix=API_PREFIX)

# 外部无需登录的签署路由，不加 /api/v1 前缀
app.include_router(contracts_public_router, prefix="/api")
app.include_router(itineraries_public_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
