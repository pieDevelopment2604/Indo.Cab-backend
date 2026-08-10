from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.fleet import router as fleet_router
from app.routes.documents import router as documents_router
from app.routes.pricing import router as pricing_router
from app.routes.bookings import router as bookings_router
from app.routes.escalations import router as escalations_router
from app.core.config import settings

app = FastAPI(
    title="Indo.Cab Backend",
    version="1.0.0",
)

# Parse ALLOWED_ORIGINS from comma-separated env string
_allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(fleet_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(pricing_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(escalations_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
