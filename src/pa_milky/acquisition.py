"""Cash-funded account purchases, distinct from trading account equity."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
import math
from .account import money

HYBRID = {'monthly_advance_replacements','monthly_plus_replacements','monthly_current_slot_replacements'}


@dataclass(frozen=True)
class AcquisitionPolicy:
    name: str
    initial_cash_usd: float
    monthly_contribution_usd: float = 0
    max_live_accounts: int = 20
    replacement_target: int = 1
    reinvest_fraction: float = 1
    restart_when_empty: bool = False
    # None keeps the inherited instant, unlimited supply of funded accounts.
    # Otherwise at most passes_per_month accounts pass per calendar month, each
    # paid when it passes. A pass not needed at once waits dormant on a shelf
    # of up to spare_capacity, and spares count toward max_live_accounts.
    spare_capacity: int | None = None
    passes_per_month: int = 0

    def __post_init__(self):
        if self.name not in {'monthly_one','monthly_two','weekly_one','quarterly_one','quarterly_three','replace','reinvest'} | HYBRID:
            raise ValueError('Unknown acquisition policy')
        if any(not math.isfinite(v) or v < 0 for v in
               (self.initial_cash_usd,self.monthly_contribution_usd)):
            raise ValueError('Funding must be finite and non-negative')
        if self.max_live_accounts < 1 or not 1 <= self.replacement_target <= self.max_live_accounts:
            raise ValueError('Invalid live-account limits')
        if not 0 <= self.reinvest_fraction <= 1:
            raise ValueError('Reinvestment fraction must be between zero and one')
        if self.spare_capacity is None:
            if self.passes_per_month:
                raise ValueError('A pass rate needs a spare shelf; set spare_capacity (0 for none)')
        elif not 0 <= self.spare_capacity < self.max_live_accounts or self.passes_per_month < 1:
            raise ValueError('Spare shelf needs 0 <= spares < live cap and at least one pass a month')


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
    filled_month_slots: set = field(default_factory=set)
    observed_deaths: int = 0
    pending_replacements: int = 0
    future_slots_used: int = 0
    replacement_events: list = field(default_factory=list)
    spares: int = 0
    pass_month: tuple = ()
    passes_this_month: int = 0
    spare_events: list = field(default_factory=list)

    @property
    def shelved(self):
        return self.policy.spare_capacity is not None

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

    def passes_left(self, at):
        if (at.year,at.month) != self.pass_month:
            self.pass_month,self.passes_this_month=(at.year,at.month),0
        return self.policy.passes_per_month-self.passes_this_month

    def obtainable(self, at, alive, fee):
        """Accounts that could go live now: spares first, then fresh passes paid from cash."""
        room=max(0,self.policy.max_live_accounts-alive)
        if not self.shelved: return min(room,int(self.cash_usd//fee))
        fresh=min(self.passes_left(at),max(0,room-self.spares),int(self.cash_usd//fee))
        return min(room,self.spares+fresh)

    def limits(self, at, alive, fee, wanted, count):
        room=max(0,self.policy.max_live_accounts-alive)
        short=count<min(wanted,room)
        flags={'capacity_limited':min(wanted,room)<wanted,'cash_limited':short}
        if self.shelved:
            free=max(0,room-self.spares)
            flags['cash_limited']=short and self.spares+min(free,int(self.cash_usd//fee))<min(wanted,room)
            flags['supply_limited']=short and self.spares+min(free,self.passes_left(at))<min(wanted,room)
        return flags

    def deploy(self, at, count, fee):
        """Put accounts live, spares first; only fresh passes are paid now."""
        shelf=min(count,self.spares)
        self.spares-=shelf
        fresh=count-shelf
        if self.shelved: self.passes_this_month+=fresh
        amount=money(fresh*fee)
        if fresh:
            self.spent_usd=money(self.spent_usd+amount)
            self.cash_event(at,'account_purchase',-amount)
        return amount

    def restock(self, at, alive, fee):
        """Pass evaluations to refill the shelf, within this month's passes, the cap and cash."""
        if not self.shelved: return 0
        room=self.policy.max_live_accounts-alive-self.spares
        n=max(0,min(self.policy.spare_capacity-self.spares,self.passes_left(at),room,int(self.cash_usd//fee)))
        if n:
            amount=money(n*fee)
            self.spares+=n
            self.passes_this_month+=n
            self.spent_usd=money(self.spent_usd+amount)
            self.cash_event(at,'spare_purchase',-amount)
            self.spare_events.append({'at':at.isoformat(),'shelved':n,'spares_after':self.spares})
        return n

    def decide(self, at, month_index, alive, account_count, fee):
        if fee <= 0: raise ValueError('Cash purchase study requires a positive fee')
        if self.policy.name in HYBRID:
            count=self.decide_hybrid(at, alive, account_count, fee)
        else:
            count=self.decide_scheduled(at, month_index, alive, fee)
        self.restock(at, alive+count, fee)
        return count

    def decide_scheduled(self, at, month_index, alive, fee):
        p=self.policy
        room=max(0,p.max_live_accounts-alive)
        wanted=0
        seed_purchase = not self.seed_bought or (p.restart_when_empty and alive == 0)
        if p.name=='monthly_one' and at.day==1: wanted=1
        elif p.name=='monthly_two' and at.day==1: wanted=2
        elif p.name=='weekly_one' and at.weekday()==0: wanted=1
        elif p.name in {'quarterly_one','quarterly_three'} and at.day==1 and month_index%3==0:
            wanted=1 if p.name=='quarterly_one' else 3
        elif p.name=='replace': wanted=max(0,p.replacement_target-alive)
        elif p.name=='reinvest':
            if seed_purchase: wanted=1
            else:
                budget=money(p.reinvest_fraction*self.received_usd-self.payout_budget_spent_usd)
                wanted=max(0,int(budget//fee))
        if not wanted: return 0
        count=min(wanted,self.obtainable(at,alive,fee))
        self.decisions.append({'at':at.isoformat(),'wanted':wanted,'bought':count,
                               **self.limits(at,alive,fee,wanted,count),'alive_before':alive})
        if count:
            amount=self.deploy(at,count,fee)
            if p.name=='reinvest' and not seed_purchase:
                self.payout_budget_spent_usd=money(self.payout_budget_spent_usd+amount)
            self.seed_bought=True
        return count

    def decide_hybrid(self, at, alive, account_count, fee):
        deaths = account_count-alive
        self.pending_replacements += deaths-self.observed_deaths
        self.observed_deaths = deaths
        advance = self.policy.name == 'monthly_advance_replacements'
        current_slot = self.policy.name == 'monthly_current_slot_replacements'
        month = (at.year,at.month)
        scheduled = at.day == 1 and (not current_slot or month not in self.filled_month_slots)
        skipped = scheduled and advance and self.future_slots_used > 0
        if skipped:
            self.future_slots_used -= 1
        # Settle existing slot debt first. Replacements now consume future dates.
        available = self.obtainable(at,alive,fee)
        wanted = self.pending_replacements + int(scheduled and not skipped)
        replaced = min(self.pending_replacements,available)
        self.pending_replacements -= replaced
        if advance:
            self.future_slots_used += replaced
        consumed_current = current_slot and replaced > 0 and month not in self.filled_month_slots
        if consumed_current:
            self.filled_month_slots.add(month)
        scheduled_bought = int(scheduled and not skipped and not consumed_current and available>replaced)
        if current_slot and scheduled_bought:
            self.filled_month_slots.add(month)
        count = replaced+scheduled_bought
        self.replacement_events.append({'at':at.isoformat(),'replacements':replaced,
            'scheduled_bought':scheduled_bought,'consumed_current_month_slot':bool(consumed_current),'scheduled_skipped_for_debt':bool(skipped),
            'pending_replacements':self.pending_replacements,'future_slots_used':self.future_slots_used})
        if consumed_current and scheduled:
            wanted -= 1
        if wanted:
            self.decisions.append({'at':at.isoformat(),'wanted':wanted,'bought':count,
                **self.limits(at,alive,fee,wanted,count),'alive_before':alive})
        if count:
            self.deploy(at,count,fee)
        return count

    def summary(self):
        out={'policy':asdict(self.policy),'owner_contributions_usd':self.contributed_usd,
             'payouts_received_usd':self.received_usd,'purchase_spend_usd':self.spent_usd,
             'ending_owner_cash_usd':self.cash_usd,
             'net_cash_created_usd':money(self.cash_usd-self.contributed_usd),
             'cash_limited_decisions':sum(d['cash_limited'] for d in self.decisions),
             'capacity_limited_decisions':sum(d['capacity_limited'] for d in self.decisions),
             'cash_identity_residual_usd':money(self.cash_usd-self.contributed_usd-self.received_usd+self.spent_usd)}
        if self.shelved:
            out.update(spares_shelved=sum(e['shelved'] for e in self.spare_events),
                       spares_unused_at_end=self.spares,
                       supply_limited_decisions=sum(d['supply_limited'] for d in self.decisions))
        return out
