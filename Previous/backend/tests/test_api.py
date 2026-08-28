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
    result=client.get("/api/v1/risk/ACC-0001"); assert result.status_code==200 and result.json()["model"]["implementation"]=="MOCK"
def test_investigation_update():
    assert len(client.get("/api/v1/investigations").json())>=10
    result=client.patch("/api/v1/investigations/CASE-0001/status",json={"status":"UNDER_INVESTIGATION"}); assert result.json()["status"]=="UNDER_INVESTIGATION"
def test_trace():
    result=client.get("/api/v1/trace/TXN-0001").json(); assert result["max_depth"]==3 and len(result["hops"])==5
def test_simulation():
    result=client.post("/api/v1/simulation/start",json={"fraud_strategy":"Rapid Pass-Through","mule_count":20,"transactions":50000,"network_depth":4,"adaptation_level":3}); assert result.status_code==201 and len(result.json()["rounds"])==4
def test_metrics_and_status():
    assert "MOCK" in client.get("/api/v1/model/metrics").json()["label"]
    assert client.get("/api/v1/system/status").json()["components"][-1]["implementation"]=="IN-MEMORY"
