from fastapi import APIRouter,Depends
from app.schemas.models import Investigation,InvestigationCreate,StatusUpdate
from app.dependencies.services import get_investigation_service
from app.services.core import InvestigationReportService
router=APIRouter(prefix="/investigations",tags=["Investigations"])
@router.get("",response_model=list[Investigation])
def list_cases(s=Depends(get_investigation_service)): return s.list()
@router.get("/{case_id}",response_model=Investigation)
def get_case(case_id:str,s=Depends(get_investigation_service)): return s.get(case_id)
@router.post("",response_model=Investigation,status_code=201)
def create_case(data:InvestigationCreate,s=Depends(get_investigation_service)): return s.create(data)
@router.patch("/{case_id}/status",response_model=Investigation)
def update_case(case_id:str,data:StatusUpdate,s=Depends(get_investigation_service)): return s.update_status(case_id,data.status)
@router.get("/{case_id}/report")
def report(case_id:str,s=Depends(get_investigation_service)): return InvestigationReportService().generate(s.get(case_id))
