from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    auth, settings as settings_router, orders, production, lots, packaging, 
    warehouse, shipments, analytics, customers, products, attachments, notifications
)

app = FastAPI(title="Demo Kimya ERP API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(settings_router.router, prefix="/settings", tags=["settings"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(production.router, prefix="/production-jobs", tags=["production"])
app.include_router(lots.router, prefix="/lots", tags=["lots"])
app.include_router(packaging.router, prefix="/packaging", tags=["packaging"])
app.include_router(warehouse.router, prefix="/warehouses", tags=["warehouses"])
app.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(attachments.router, prefix="/attachments", tags=["attachments"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

@app.get("/")
async def root():
    return {"message": "Demo Kimya ERP API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}