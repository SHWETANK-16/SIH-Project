from copy import deepcopy
from app.data.synthetic import ACCOUNTS, TRANSACTIONS, NETWORKS, INVESTIGATIONS
from app.repositories.interfaces.repositories import *

class InMemoryAccountRepository(AccountRepository):
    def __init__(self): self.items=deepcopy(ACCOUNTS)
    def list(self): return self.items
    def get(self,id): return next((x for x in self.items if x.account_id==id),None)
class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self): self.items=deepcopy(TRANSACTIONS)
    def list(self): return self.items
    def get(self,id): return next((x for x in self.items if x.transaction_id==id),None)
    def add(self,x): self.items.insert(0,x); return x
class InMemoryNetworkRepository(NetworkRepository):
    def __init__(self): self.items=deepcopy(NETWORKS)
    def list(self): return self.items
    def get(self,id): return next((x for x in self.items if x.network_id==id),None)
class InMemoryInvestigationRepository(InvestigationRepository):
    def __init__(self): self.items=deepcopy(INVESTIGATIONS)
    def list(self): return self.items
    def get(self,id): return next((x for x in self.items if x.case_id==id),None)
    def add(self,x): self.items.insert(0,x); return x
    def update(self,x): self.items[self.items.index(next(i for i in self.items if i.case_id==x.case_id))]=x; return x
