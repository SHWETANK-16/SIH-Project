from fastapi import APIRouter, Depends
from app.schemas.models import MoneyFlow
from app.dependencies.services import get_tracing_service
from app.services.core import TracingService

router = APIRouter(tags=["Money Flow"])

@router.get("/trace/{transaction_id}", response_model=MoneyFlow)
def trace(transaction_id: str, service: TracingService = Depends(get_tracing_service)):
    return service.trace(transaction_id)
