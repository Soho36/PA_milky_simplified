"""Cash-funded account purchases, distinct from trading account equity."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
import math
from .account import money


@dataclass(frozen=True)
class AcquisitionPolicy:
    name: str
    initial_cash_usd: float
    monthly_contribution_usd: float = 0
    max_live_accounts: int = 20
    replacement_target: int = 1
    reinvest_fraction: float = 1
    restart_when_empty: bool = False

    def __post_init__(self):
        if self.name not in {'monthly_one','quarterly_one','quarterly_three','replace','reinvest'}:
            raise ValueError('Unknown acquisition policy')
        if any(not math.isfinite(v) or v < 0 for v in
               (self.initial_cash_usd,self.monthly_contribution_usd)):
            raise ValueError('Funding must be finite and non-negative')
        if self.max_live_accounts < 1 or not 1 <= self.replacement_target <= self.max_live_accounts:
            raise ValueError('Invalid live-account limits')
        if not 0 <= self.reinvest_fraction <= 1:
            raise ValueError('Reinvestment fraction must be between zero and one')


@dataclass
class AcquisitionLedger:
    policy: AcquisitionPolicy
    cash_usd: float = 0
    contributed_usd: float = 0
    received_usd: float = 0
    spent_usd: float = 0
    payout_budget_spent_usd: float = 0
    seed_bought: bool = False
    last_receipt_index: int = 0
    funded_months: set = field(default_factory=set)
    cash_events: list = field(default_factory=list)
    decisions: list = field(default_factory=list)

    def cash_event(self, at, kind, amount):
        self.cash_usd = money(self.cash_usd + amount)
        if self.cash_usd < 0:
            raise ValueError('Owner cash became negative')
        self.cash_events.append({'at':at.isoformat(),'kind':kind,'amount_usd':amount,
                                 'cash_after_usd':self.cash_usd})

    def fund(self, at):
        key=(at.year,at.month)
        if key in self.funded_months: return
        amount = self.policy.initial_cash_usd if not self.funded_months else self.policy.monthly_contribution_usd
        self.funded_months.add(key)
        self.contributed_usd=money(self.contributed_usd+amount)
        self.cash_event(at,'owner_contribution',amount)

    def receive(self, payouts):
        for e in payouts[self.last_receipt_index:]:
            self.received_usd=money(self.received_usd+e.received_usd)
            self.cash_event(e.at,'payout_received',e.received_usd)
        self.last_receipt_index=len(payouts)

    def decide(self, at, month_index, alive, account_count, fee):
        if fee <= 0: raise ValueError('Cash purchase study requires a positive fee')
        p=self.policy
        room=max(0,p.max_live_accounts-alive)
        wanted=0
        seed_purchase = not self.seed_bought or (p.restart_when_empty and alive == 0)
        if p.name=='monthly_one' and at.day==1: wanted=1
        elif p.name in {'quarterly_one','quarterly_three'} and at.day==1 and month_index%3==0:
            wanted=1 if p.name=='quarterly_one' else 3
        elif p.name=='replace': wanted=max(0,p.replacement_target-alive)
        elif p.name=='reinvest':
            if seed_purchase: wanted=1
            else:
                budget=money(p.reinvest_fraction*self.received_usd-self.payout_budget_spent_usd)
                wanted=max(0,int(budget//fee))
        if not wanted: return 0
        count=min(wanted,room,int(self.cash_usd//fee))
        self.decisions.append({'at':at.isoformat(),'wanted':wanted,'bought':count,
                               'capacity_limited':min(wanted,room)<wanted,
                               'cash_limited':count<min(wanted,room),'alive_before':alive})
        if count:
            amount=money(count*fee)
            if p.name=='reinvest' and not seed_purchase:
                self.payout_budget_spent_usd=money(self.payout_budget_spent_usd+amount)
            self.seed_bought=True
            self.spent_usd=money(self.spent_usd+amount)
            self.cash_event(at,'account_purchase',-amount)
        return count

    def summary(self):
        return {'policy':asdict(self.policy),'owner_contributions_usd':self.contributed_usd,
                'payouts_received_usd':self.received_usd,'purchase_spend_usd':self.spent_usd,
                'ending_owner_cash_usd':self.cash_usd,
                'net_cash_created_usd':money(self.cash_usd-self.contributed_usd),
                'cash_limited_decisions':sum(d['cash_limited'] for d in self.decisions),
                'capacity_limited_decisions':sum(d['capacity_limited'] for d in self.decisions),
                'cash_identity_residual_usd':money(self.cash_usd-self.contributed_usd-self.received_usd+self.spent_usd)}
