from app.data.synthetic import EXPLANATION
from app.schemas.models import Explanation

class ExplainabilityService:
    """Future home of SHAP, graph and rule explanations."""
    def explain(self, *_: object) -> Explanation: return EXPLANATION.model_copy(deep=True)
    def status(self): return {"implementation":"MOCK","status":"READY","version":"0.1.0"}
