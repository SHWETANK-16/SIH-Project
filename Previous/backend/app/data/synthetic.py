"""Single deterministic source of truth for the connected demo dataset."""
from datetime import datetime, timedelta, timezone
from app.schemas.models import *

NOW = datetime(2026, 8, 24, 10, 30, tzinfo=timezone.utc)
INDICATORS = ["Rapid pass-through", "Fan-in / fan-out pattern", "Behaviour deviation", "Suspicious network connections"]

def level(score: float) -> RiskLevel:
    return RiskLevel.CRITICAL if score >= 85 else RiskLevel.HIGH if score >= 70 else RiskLevel.MEDIUM if score >= 40 else RiskLevel.LOW

def build_transactions() -> list[Transaction]:
    rows=[]
    for i in range(1, 121):
        network=(i-1)%4+1; start=(network-1)*10+1
        source=start+(i%9); destination=start+((i+2+(i//12))%10)
        if source==destination: destination=start+((destination-start+1)%10)
        amount=float(12500 + ((i*7919)%145000)); risk=round(34+((i*13+network*7)%64),1)
        rows.append(Transaction(transaction_id=f"TXN-{i:04d}",source_account_id=f"ACC-{source:04d}",destination_account_id=f"ACC-{destination:04d}",amount=amount,timestamp=NOW-timedelta(hours=i*3),transaction_type=["IMPS","UPI","NEFT","RTGS"][i%4],risk_score=risk,risk_level=level(risk),status="FLAGGED" if risk>=70 else "MONITORED",network_id=f"NET-{network:03d}"))
    # Preserve a memorable branching demo trail for TXN-0001.
    trail=[(1,1,2,50000),(2,2,3,47000),(3,3,4,30000),(4,3,5,10000),(5,3,6,7000)]
    for idx,s,d,a in trail:
        rows[idx-1]=Transaction(transaction_id=f"TXN-{idx:04d}",source_account_id=f"ACC-{s:04d}",destination_account_id=f"ACC-{d:04d}",amount=a,timestamp=NOW-timedelta(minutes=idx*18),transaction_type="IMPS",risk_score=96-idx*2,risk_level=RiskLevel.CRITICAL,status="FLAGGED",network_id="NET-001")
    return rows

TRANSACTIONS=build_transactions()

def build_accounts() -> list[Account]:
    accounts=[]
    for i in range(1,41):
        aid=f"ACC-{i:04d}"; incoming=sum(t.amount for t in TRANSACTIONS if t.destination_account_id==aid); outgoing=sum(t.amount for t in TRANSACTIONS if t.source_account_id==aid)
        linked=[t for t in TRANSACTIONS if aid in (t.source_account_id,t.destination_account_id)]; score=round(max([t.risk_score for t in linked] or [25])*.92,1)
        beneficiaries=len({t.destination_account_id for t in linked if t.source_account_id==aid})
        accounts.append(Account(account_id=aid,account_type="Current" if i%3==0 else "Savings",created_at=NOW-timedelta(days=230+i*19),transaction_count=len(linked),incoming_amount=incoming,outgoing_amount=outgoing,beneficiaries=beneficiaries,network_size=10,risk_score=score,risk_level=level(score),status="REVIEW" if score>=70 else "MONITORED"))
    return accounts
ACCOUNTS=build_accounts()

def build_networks() -> list[Network]:
    result=[]
    for n in range(1,5):
        lo=(n-1)*10+1; ids={f"ACC-{i:04d}" for i in range(lo,lo+10)}; tx=[t for t in TRANSACTIONS if t.source_account_id in ids and t.destination_account_id in ids]
        nodes=[]
        for a in [x for x in ACCOUNTS if x.account_id in ids]:
            nodes.append(NetworkNode(id=a.account_id,label=("Origin " if a.account_id==f"ACC-{lo:04d}" else "Account ")+a.account_id,risk_score=a.risk_score,risk_level=a.risk_level,type="origin" if a.account_id==f"ACC-{lo:04d}" else "account",transaction_count=a.transaction_count,incoming=a.incoming_amount,outgoing=a.outgoing_amount,network_degree=min(9,a.transaction_count),fan_in=round(.5+(int(a.account_id[-2:])%5)/10,2),fan_out=round(.55+(int(a.account_id[-2:])%4)/10,2),behaviour_deviation=round(2.8+(int(a.account_id[-2:])%8)*.8,1),indicators=INDICATORS[:2+(n%3)]))
        edges=[NetworkEdge(source=t.source_account_id,target=t.destination_account_id,amount=t.amount,timestamp=t.timestamp,transaction_id=t.transaction_id,risk_level=t.risk_level,hop=1+(i%4)) for i,t in enumerate(tx[:18])]
        score=float(94-(n-1)*7)
        result.append(Network(network_id=f"NET-{n:03d}",name=["Cascade Relay","Layered Fan-Out","Dormant Reactivation","Circular Settlement"][n-1],risk_score=score,risk_level=level(score),node_count=len(nodes),edge_count=len(edges),estimated_flow=sum(e.amount for e in edges),key_indicators=INDICATORS[:3+(n%2)],nodes=nodes,edges=edges,discovered_at=NOW-timedelta(days=n*2)))
    return result
NETWORKS=build_networks()

EXPLANATION=Explanation(summary="Multiple synthetic indicators warrant investigator review.",factors=[ExplanationFactor(name="Pass-through ratio",impact="high",description="A large share of received funds moved onward rapidly."),ExplanationFactor(name="Behaviour deviation",impact="high",description="Recent demonstration activity differs from its synthetic baseline."),ExplanationFactor(name="Network connectivity",impact="medium",description="The account connects to several higher-risk demo entities.")])

def build_investigations() -> list[Investigation]:
    rows=[]
    statuses=list(InvestigationStatus)
    for i in range(1,13):
        net=NETWORKS[(i-1)%4]; risk=[RiskLevel.CRITICAL,RiskLevel.HIGH,RiskLevel.HIGH,RiskLevel.MEDIUM][(i-1)%4]
        rows.append(Investigation(case_id=f"CASE-{i:04d}",title=f"{net.name} review · cluster {i}",risk_level=risk,priority=risk,network_id=net.network_id,network_size=net.node_count,estimated_suspicious_flow=net.estimated_flow*(.45+i/30),related_accounts=[x.id for x in net.nodes[:5]],key_indicators=net.key_indicators,created_at=NOW-timedelta(days=i*2),updated_at=NOW-timedelta(hours=i*4),status=statuses[(i-1)%len(statuses)],explanation=EXPLANATION,transaction_references=[x.transaction_id for x in net.edges[:5]]))
    return rows
INVESTIGATIONS=build_investigations()

def build_trace(transaction_id: str) -> MoneyFlow:
    base=TRANSACTIONS[0]
    txs=TRANSACTIONS[:5] if transaction_id in {"TXN-0001","ACC-0001"} else [next((x for x in TRANSACTIONS if x.transaction_id==transaction_id),base)]
    cumulative=0; hops=[]
    for i,t in enumerate(txs):
        cumulative+=t.amount; hop=1 if i==0 else 2 if i==1 else 3
        hops.append(MoneyFlowHop(source=t.source_account_id,destination=t.destination_account_id,amount=t.amount,timestamp=t.timestamp,transaction_id=t.transaction_id,hop_number=hop,risk_level=t.risk_level,relationship_type="TRANSFER",cumulative_flow=cumulative))
    return MoneyFlow(trace_id=f"TRACE-{transaction_id}",root_transaction_id=txs[0].transaction_id,total_traced=sum(t.amount for t in txs),max_depth=max(h.hop_number for h in hops),hops=hops)
