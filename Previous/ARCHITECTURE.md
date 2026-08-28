# Architecture

## Runtime flow

The React frontend only talks through domain service modules backed by one API client. FastAPI routes validate Pydantic contracts and delegate immediately to application services. Routes contain no engine or repository logic.

```text
Financial event / UI request
        ↓
React domain service → FastAPI /api/v1 route
        ↓
TransactionService / entity service / workflow service
        ↓
FeatureEngine.extract_features
        ↓
XGBoostEngine.predict
        ↓
GraphEngine.get_network_context
        ↓
FraudIntelligenceEngine.assess
        ↓
ExplainabilityService.explain
        ↓
typed RiskResult → investigation UI
```

`BehaviourProfiler`, `NetworkDiscoveryService`, `InvestigationPriorityService`, and `InvestigationReportService` are explicit service boundaries. Their baseline behavior is deliberately small.

## Replacing mock engines

Contracts live in `backend/app/engines/interfaces/`; mock implementations live in `backend/app/engines/mock/`. Add (for example) `RealGraphEngine(GraphEngine)` in a new implementation package. Implement every abstract method, then change only `get_graph_engine()` in `backend/app/dependencies/services.py`. Routes, services, response schemas, tests of the public contract, and the frontend remain unchanged. Apply the same pattern to all four engines.

Future implementations must preserve deterministic validation, avoid leaking sensitive data into logs, expose implementation metadata, and return the existing contract types.

## Storage evolution

Today, repository interfaces resolve to process-local in-memory repositories seeded from one connected synthetic dataset. There is no persistence.

```text
Repository contracts
  ├─ today: in-memory synthetic state
  └─ future
      ├─ structured events → PostgreSQL / distributed SQL adapter
      ├─ relationships → graph infrastructure adapter
      └─ training history → object/data-lake adapter
```

A future adapter should implement the relevant repository interface and change dependency wiring only. **No database, ORM, migration, Redis, or graph database exists in this baseline.**

## Scale and trust boundaries

The graph renderer intentionally displays small neighborhoods. National-scale operation would require server-side filtering, pagination, lazy expansion, and dedicated graph infrastructure. Synthetic risk means “review this pattern,” never “this entity is criminal.”
