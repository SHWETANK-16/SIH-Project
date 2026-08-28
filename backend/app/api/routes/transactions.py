from fastapi import APIRouter, Depends
from app.schemas.models import Transaction, TransactionCreate, RiskResult
from app.services.core import TransactionService
from app.dependencies.services import get_transaction_service
router=APIRouter(prefix="/transactions",tags=["Transactions"])
@router.get("",response_model=list[Transaction],summary="List synthetic transactions")
def list_transactions(s:TransactionService=Depends(get_transaction_service)): return s.list()
@router.get("/{transaction_id}",response_model=Transaction)
def get_transaction(transaction_id:str,s:TransactionService=Depends(get_transaction_service)): return s.get(transaction_id)
@router.post("",response_model=RiskResult,status_code=201,summary="Process a transaction through the mock intelligence pipeline")
def create_transaction(data:TransactionCreate,s:TransactionService=Depends(get_transaction_service)): return s.create(data)
