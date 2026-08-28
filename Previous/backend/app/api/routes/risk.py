from fastapi import APIRouter,Depends
from app.schemas.models import RiskResult,RiskCheckRequest
from app.services.core import TransactionService
from app.dependencies.services import get_transaction_service
from app.exceptions.handlers import NotFoundError
router=APIRouter(tags=["Risk Intelligence"])
@router.get("/risk/{account_id}",response_model=RiskResult)
def account_risk(account_id:str,s:TransactionService=Depends(get_transaction_service)): return s.assess_account(account_id)
@router.post("/risk-check",response_model=RiskResult)
def risk_check(data:RiskCheckRequest,s:TransactionService=Depends(get_transaction_service)):
    if data.transaction: return s.create(data.transaction)
    if data.account_id: return s.assess_account(data.account_id)
    raise NotFoundError("RISK_TARGET_REQUIRED","Provide an account_id or transaction.")
