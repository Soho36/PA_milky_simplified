"""Study-local sleeve assignment and reserve policies; core engine is unchanged."""
from collections import Counter
from dataclasses import dataclass, field

from pa_milky.policy import WithdrawalPolicy
from pa_milky.rr_diversification import RRRouter


@dataclass
class Sleeves:
    definitions: list
    assigned: dict = field(default_factory=dict)

    def assign(self, accounts):
        live = Counter(self.assigned[a.account_id] for a in accounts
                       if a.alive and a.account_id in self.assigned)
        for account in accounts:
            if account.account_id not in self.assigned:
                group = min(range(len(self.definitions)), key=lambda i: live[i])
                self.assigned[account.account_id] = group
                live[group] += int(account.alive)

    def definition(self, account_id):
        return self.definitions[self.assigned[account_id]]


class SleeveRouter(RRRouter):
    def __init__(self, *args, sleeves, **kwargs):
        self.sleeves = sleeves
        super().__init__(*args, **kwargs)

    def assign(self, accounts):
        self.accounts = accounts
        self.sleeves.assign(accounts)
        self.account_rr = {a.account_id: self.sleeves.definition(a.account_id)['rr'] for a in accounts}

    def summary(self):
        return {**super().summary(), 'account_sleeve': dict(self.sleeves.assigned)}


class LadderPolicy(WithdrawalPolicy):
    def __init__(self, *, sleeves, floor_balance, **kwargs):
        super().__init__(min_retained_balance_usd=None, **kwargs)
        object.__setattr__(self, 'sleeves', sleeves)
        object.__setattr__(self, 'floor_balance', floor_balance)

    def requested_usd(self, account, *, firm_minimum_usd):
        want = super().requested_usd(account, firm_minimum_usd=firm_minimum_usd)
        threshold = self.floor_balance + self.sleeves.definition(account.account_id)['reserve']
        return min(want, max(0.0, round(account.balance_usd-threshold, 2)))
