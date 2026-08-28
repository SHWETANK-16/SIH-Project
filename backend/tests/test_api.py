from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health(): assert client.get("/health").json()["status"]=="healthy"
def test_transactions():
    rows=client.get("/api/v1/transactions"); assert rows.status_code==200 and len(rows.json())>=120
    payload={"source_account_id":"ACC-0001","destination_account_id":"ACC-0002","amount":50000,"timestamp":"2026-08-24T10:00:00Z","transaction_type":"IMPS"}
    result=client.post("/api/v1/transactions",json=payload); assert result.status_code==201 and result.json()["synthetic"] is True
def test_accounts(): assert len(client.get("/api/v1/accounts").json())==40
def test_account_not_found_contract():
    result=client.get("/api/v1/accounts/ACC-9999"); assert result.status_code==404 and result.json()["error"]["code"]=="ACCOUNT_NOT_FOUND"
def test_networks():
    rows=client.get("/api/v1/networks").json(); assert len(rows)==4 and rows[0]["edges"][0]["transaction_id"]
def test_risk_pipeline():
    result=client.get("/api/v1/risk/ACC-0001"); assert result.status_code==200
    body=result.json()
    # XGBOOST_HYBRID when a trained artifact is loaded, CALIBRATED_ML_FALLBACK when
    # xgboost is unavailable. Both are valid deployments of the same contract.
    assert body["model"]["implementation"] in {"XGBOOST_HYBRID","CALIBRATED_ML_FALLBACK","CALIBRATED_ML"}
    assert 0<=body["risk_score"]<=100 and body["explanation"]["factors"]
def test_investigation_update():
    assert len(client.get("/api/v1/investigations").json())>=10
    result=client.patch("/api/v1/investigations/CASE-0001/status",json={"status":"UNDER_INVESTIGATION"}); assert result.json()["status"]=="UNDER_INVESTIGATION"
def test_trace():
    result=client.get("/api/v1/trace/TXN-0001").json(); assert result["max_depth"]==3 and len(result["hops"])==5
def test_simulation():
    result=client.post("/api/v1/simulation/start",json={"fraud_strategy":"Rapid Pass-Through","mule_count":20,"transactions":50000,"network_depth":4,"adaptation_level":3}); assert result.status_code==201 and len(result.json()["rounds"])==4
def test_metrics_and_status():
    metrics=client.get("/api/v1/model/metrics").json()
    if metrics["measured"]:
        # Real held-out numbers must be plausible, and the ablation study must show
        # the graph layer adding signal rather than being decorative.
        assert 0<metrics["precision"]<=1 and 0<metrics["pr_auc"]<=1
        assert "TRAINED" in metrics["label"] and len(metrics["comparisons"])>=2
        assert metrics["comparisons"][-1]["score"]>=metrics["comparisons"][0]["score"]
    else:
        assert "MOCK" in metrics["label"]
    assert client.get("/api/v1/system/status").json()["components"][-1]["implementation"]=="IN-MEMORY"
def test_model_features():
    body=client.get("/api/v1/model/features").json(); assert body["n_features"]>=1
    assert body["importances"]==sorted(body["importances"],key=lambda r:r["importance"],reverse=True)
