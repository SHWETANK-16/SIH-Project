from fastapi import APIRouter
from app.api.routes import transactions,accounts,networks,risk,investigations,tracing,simulation,system
api_router=APIRouter()
for route in [transactions.router,accounts.router,networks.router,risk.router,investigations.router,tracing.router,simulation.router,system.router]: api_router.include_router(route)
