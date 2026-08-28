from fastapi import APIRouter,Depends
from app.schemas.models import Account
from app.dependencies.services import get_account_service
router=APIRouter(prefix="/accounts",tags=["Accounts"])
@router.get("",response_model=list[Account])
def list_accounts(s=Depends(get_account_service)): return s.list()
@router.get("/{account_id}",response_model=Account)
def get_account(account_id:str,s=Depends(get_account_service)): return s.get(account_id)
