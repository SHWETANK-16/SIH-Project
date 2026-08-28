from fastapi import APIRouter,Depends
from app.schemas.models import Network
from app.dependencies.services import get_network_service
router=APIRouter(prefix="/networks",tags=["Networks"])
@router.get("",response_model=list[Network])
def list_networks(s=Depends(get_network_service)): return s.list()
@router.get("/{network_id}",response_model=Network)
def get_network(network_id:str,s=Depends(get_network_service)): return s.get(network_id)
