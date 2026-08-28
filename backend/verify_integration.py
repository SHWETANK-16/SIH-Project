"""End-to-end health check for a running FraudTracer backend.

Verifies not just that endpoints respond, but that the XGBoost integration is
actually live — trained model loaded, real metrics, TreeSHAP attribution present,
guardrails firing, and score bands agreeing with the model's own verdict.

Start the server first, then::

    cd backend
    python -m uvicorn app.main:app --reload     # terminal 1
    python verify_integration.py                # terminal 2

Optional: ``python verify_integration.py --url http://localhost:8000``

Exit code 0 = everything passed. 1 = something needs attention.
"""
from __future__ import annotations

import argparse
import sys

try:
    import httpx
except ImportError:
    print("error: httpx not installed. Run: pip install -r requirements.txt")
    raise SystemExit(1)

PASS, FAIL, WARN, INFO = "PASS", "FAIL", "WARN", "INFO"
results: list[tuple[str, str, str]] = []

GREEN, RED, YELLOW, BLUE, DIM, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[2m", "\033[0m",
)
COLOUR = {PASS: GREEN, FAIL: RED, WARN: YELLOW, INFO: BLUE}


def record(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))
    print(f"  {COLOUR[status]}{status:<4}{RESET} {name}" + (f"  {DIM}{detail}{RESET}" if detail else ""))


def section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def check(name: str, condition: bool, ok: str = "", bad: str = "") -> bool:
    record(PASS if condition else FAIL, name, ok if condition else bad)
    return condition


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a running FraudTracer backend.")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend base URL.")
    args = parser.parse_args()
    base = args.url.rstrip("/")
    api = f"{base}/api/v1"

    print(f"Verifying {base}")

    try:
        client = httpx.Client(base_url=base, timeout=30.0)
    except Exception as exc:
        print(f"could not create client: {exc}")
        return 1

    # ---------------------------------------------------------------- #
    section("1. Server reachable")
    # ---------------------------------------------------------------- #
    try:
        health = client.get("/health")
    except httpx.ConnectError:
        print(f"  {RED}FAIL{RESET} cannot connect to {base}")
        print(f"\n  Is the server running? Start it with:")
        print(f"    cd backend && python -m uvicorn app.main:app --reload")
        return 1

    check("GET /health returns 200", health.status_code == 200, f"status={health.status_code}")
    body = health.json()
    check("service reports healthy", body.get("status") == "healthy", body.get("status", "?"))

    # ---------------------------------------------------------------- #
    section("2. Data layer")
    # ---------------------------------------------------------------- #
    accounts = client.get(f"{api}/accounts").json()
    check("40 accounts seeded", len(accounts) == 40, f"got {len(accounts)}")

    transactions = client.get(f"{api}/transactions").json()
    check("at least 120 transactions", len(transactions) >= 120, f"got {len(transactions)}")

    networks = client.get(f"{api}/networks").json()
    check("4 networks with edges", len(networks) == 4 and bool(networks[0].get("edges")), f"got {len(networks)}")

    cases = client.get(f"{api}/investigations").json()
    check("investigation cases present", len(cases) >= 10, f"got {len(cases)}")

    missing = client.get(f"{api}/accounts/ACC-9999")
    check(
        "404 contract is structured",
        missing.status_code == 404 and missing.json().get("error", {}).get("code") == "ACCOUNT_NOT_FOUND",
        f"status={missing.status_code}",
    )

    # ---------------------------------------------------------------- #
    section("3. XGBoost engine loaded")
    # ---------------------------------------------------------------- #
    status = client.get(f"{api}/system/status").json()
    engine = next((c for c in status["components"] if "XGBoost" in c["component"]), None)

    if engine is None:
        record(FAIL, "XGBoost component present in status", "not found")
        return 1

    impl = engine["implementation"]
    trained = impl == "XGBOOST_HYBRID"

    if trained:
        record(PASS, "trained model is serving", f"{impl} / {engine['status']}")
    else:
        record(FAIL, "trained model is serving", f"got {impl} — falling back to rules")
        print(f"\n  {YELLOW}The model did not load.{RESET} Fix with:")
        print("    cd backend && python -m app.ml.train_xgboost")
        print("  Then restart the server and re-run this script.")

    record(
        INFO if status["overall"] != "READY" else PASS,
        f"overall system status: {status['overall']}",
        "" if status["overall"] == "READY" else "some component is degraded",
    )

    # ---------------------------------------------------------------- #
    section("4. Real metrics, not placeholders")
    # ---------------------------------------------------------------- #
    metrics = client.get(f"{api}/model/metrics").json()
    measured = metrics.get("measured", False)

    if not check("metrics are measured", measured, "real held-out numbers", "still serving MOCK placeholders"):
        pass
    else:
        record(
            INFO,
            "held-out performance",
            f"precision {metrics['precision']} · recall {metrics['recall']} · "
            f"F1 {metrics['f1']} · PR-AUC {metrics['pr_auc']} · FPR {metrics['false_positive_rate']}",
        )
        check("label declares synthetic training", "TRAINED" in metrics.get("label", ""), metrics.get("label", "")[:48])
        check(
            "PR-AUC is plausible, not leaked",
            0.70 < metrics["pr_auc"] < 0.999,
            f"{metrics['pr_auc']}",
            f"{metrics['pr_auc']} — suspicious, check for label leakage",
        )
        check("confusion matrix populated", sum(metrics.get("confusion", {}).values()) > 0)

        comparisons = metrics.get("comparisons", [])
        check("ablation study has 3 layers", len(comparisons) == 3, f"got {len(comparisons)}")
        if len(comparisons) == 3:
            first, last = comparisons[0]["score"], comparisons[-1]["score"]
            uplift = round(last - first, 4)
            if uplift > 0.01:
                record(PASS, "graph layer adds signal", f"+{uplift} PR-AUC")
            else:
                record(
                    WARN,
                    "graph layer adds little",
                    f"{first} -> {last} (+{uplift}) — chart will look flat; explain why",
                )

        rates = metrics.get("archetype_flag_rate", {})
        if rates:
            for legit in ("merchant_collector", "payroll_distributor"):
                if legit in rates:
                    rate = rates[legit]
                    record(
                        PASS if rate < 0.15 else FAIL,
                        f"hard negative '{legit}' not over-flagged",
                        f"flag rate {rate:.1%}",
                    )
            mules = [k for k in ("rapid_relay", "fanout_smurf", "fanin_aggregator", "circular_layering") if k in rates]
            if mules:
                worst = min(rates[m] for m in mules)
                record(
                    PASS if worst > 0.85 else WARN,
                    "all mule typologies caught",
                    f"lowest recall {worst:.1%}",
                )

    # ---------------------------------------------------------------- #
    section("5. Feature importance endpoint")
    # ---------------------------------------------------------------- #
    features = client.get(f"{api}/model/features").json()
    importances = features.get("importances", [])
    check("12 features reported", len(importances) == 12, f"got {len(importances)}")
    check(
        "sorted by importance descending",
        [r["importance"] for r in importances] == sorted((r["importance"] for r in importances), reverse=True),
    )
    if importances:
        top = ", ".join(f"{r['feature']} {r['importance']:.0%}" for r in importances[:3])
        record(INFO, "top drivers overall", top)

    # ---------------------------------------------------------------- #
    section("6. Scoring pipeline and TreeSHAP")
    # ---------------------------------------------------------------- #
    risk = client.get(f"{api}/risk/ACC-0001")
    if not check("GET /risk/{id} returns 200", risk.status_code == 200, f"status={risk.status_code}"):
        return 1

    result = risk.json()
    model = result["model"]
    check("score within 0-100", 0 <= result["risk_score"] <= 100, f"{result['risk_score']}")
    check("explanation has factors", bool(result["explanation"]["factors"]), f"{len(result['explanation']['factors'])} factors")
    record(INFO, "example assessment", f"ACC-0001 -> {result['risk_score']} ({result['risk_level']})")

    if trained:
        check("model probability exposed", model.get("probability") is not None, str(model.get("probability")))
        check("rules score exposed alongside", model.get("rules_score") is not None, str(model.get("rules_score")))
        check(
            "blend weight is active",
            model.get("model_weight") not in (None, 0),
            f"model_weight={model.get('model_weight')}",
        )

        drivers = model.get("top_drivers", [])
        check("TreeSHAP drivers returned", bool(drivers), f"{len(drivers)} drivers")
        check("attribution method is native", model.get("shap_method") == "xgboost_native_treeshap", str(model.get("shap_method")))

        if drivers:
            shares = [d["share"] for d in drivers]
            check("drivers ranked by magnitude", shares == sorted(shares, reverse=True))
            top = drivers[0]
            record(INFO, "strongest driver", f"{top['label']} ({top['direction']}, {top['share']:.0%} of attribution)")

        # The whole point of threshold anchoring: verdict and band cannot disagree.
        if model.get("flagged") is not None and model.get("model_score") is not None:
            if model["flagged"]:
                check(
                    "flagged row lands in HIGH band or above",
                    model["model_score"] >= 70.0,
                    f"model_score={model['model_score']}",
                    f"model_score={model['model_score']} but model flagged it — anchoring broken",
                )
            else:
                check(
                    "unflagged row stays below HIGH",
                    model["model_score"] < 70.0,
                    f"model_score={model['model_score']}",
                    f"model_score={model['model_score']} but model did not flag it",
                )

    # ---------------------------------------------------------------- #
    section("7. Guardrails and live scoring")
    # ---------------------------------------------------------------- #
    created = client.post(
        f"{api}/transactions",
        json={
            "source_account_id": "ACC-0001",
            "destination_account_id": "ACC-0002",
            "amount": 480000,
            "timestamp": "2026-08-26T10:00:00Z",
            "transaction_type": "IMPS",
        },
    )
    check("POST /transactions scores a new row", created.status_code == 201, f"status={created.status_code}")
    if created.status_code == 201:
        new = created.json()
        record(INFO, "high-value transfer scored", f"{new['risk_score']} ({new['risk_level']})")
        rails = new["model"].get("guardrails_applied", [])
        record(INFO, "guardrails applied" if rails else "no guardrail triggered", "; ".join(rails) if rails else "score came from the blend alone")

    trace = client.get(f"{api}/trace/TXN-0001").json()
    check("multi-hop trace works", bool(trace.get("hops")), f"{len(trace.get('hops', []))} hops, depth {trace.get('max_depth')}")

    sim = client.post(
        f"{api}/simulation/start",
        json={"fraud_strategy": "Rapid Pass-Through", "mule_count": 20, "transactions": 50000, "network_depth": 4, "adaptation_level": 3},
    )
    check("simulator runs", sim.status_code == 201 and len(sim.json().get("rounds", [])) == 4, f"status={sim.status_code}")

    # ---------------------------------------------------------------- #
    # Summary
    # ---------------------------------------------------------------- #
    passed = sum(1 for s, _, _ in results if s == PASS)
    failed = [(n, d) for s, n, d in results if s == FAIL]
    warned = [(n, d) for s, n, d in results if s == WARN]

    print("\n" + "=" * 62)
    print(f"{passed} passed · {len(failed)} failed · {len(warned)} warnings")

    if warned:
        print(f"\n{YELLOW}Worth a look:{RESET}")
        for name, detail in warned:
            print(f"  - {name}: {detail}")

    if failed:
        print(f"\n{RED}Failed:{RESET}")
        for name, detail in failed:
            print(f"  - {name}: {detail}")
        print("\nSomething needs attention.")
        return 1

    print(f"\n{GREEN}Everything checks out.{RESET} The trained model is serving, metrics are")
    print("measured, and TreeSHAP attribution is reaching the API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
