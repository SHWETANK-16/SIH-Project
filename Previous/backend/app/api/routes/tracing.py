from fastapi import APIRouter
from app.schemas.models import MoneyFlow
from app.services.core import TracingService
router=APIRouter(tags=["Money Flow"])
@router.get("/trace/{transaction_id}",response_model=MoneyFlow)
def trace(transaction_id:str): return TracingService().trace(transaction_id)
