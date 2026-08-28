from fastapi import APIRouter,Depends
from app.schemas.models import Simulation,SimulationRequest
from app.dependencies.services import get_simulation_service
router=APIRouter(prefix="/simulation",tags=["Simulation"])
@router.post("/start",response_model=Simulation,status_code=201)
def start(data:SimulationRequest,s=Depends(get_simulation_service)): return s.start(data)
@router.get("/{simulation_id}",response_model=Simulation)
def get(simulation_id:str,s=Depends(get_simulation_service)): return s.get(simulation_id)
