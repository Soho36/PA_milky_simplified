"""Cash-funded account purchases, distinct from trading account equity."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
import math
from .account import money
from .evaluation import Evaluation, EvaluationSpec, Router

HYBRID = {'monthly_advance_replacements','monthly_plus_replacements','monthly_current_slot_replacements'}
IN_FLIGHT = ('running','blown','passed')


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
    # Evaluation supply replaces the pass rate: funded accounts come only from
    # evaluations traded on the tape, at most evaluations_at_once running and
    # started only while short. Each one in flight holds a seat for its pass.
    evaluation: EvaluationSpec | None = None
    evaluations_at_once: int = 0
    persistent_demand: bool = False
    evaluation_start_interval_days: int = 0  # 0 batches; otherwise one new subscription per interval
    evaluations_reserve_seats: bool = True
    # Operational sensitivity: pay at the first daily check after passing or
    # abandon the pass. This is a chosen policy, not a firm's legal deadline.
    activate_on_first_check: bool = False

    def __post_init__(self):
        if (not isinstance(self.evaluation_start_interval_days, int)
                or self.evaluation_start_interval_days < 0):
            raise ValueError('Evaluation start interval must be a non-negative integer')
        if self.persistent_demand and self.name != 'monthly_current_slot_replacements':
            raise ValueError('Persistent demand currently supports current-slot replacements only')
        if self.evaluation is None and (self.persistent_demand or self.evaluation_start_interval_days
                                         or not self.evaluations_reserve_seats or self.activate_on_first_check):
            raise ValueError('Pipeline settings require evaluation supply')
        if self.name not in {'monthly_one','monthly_two','weekly_one','quarterly_one','quarterly_three','replace','reinvest'} | HYBRID:
            raise ValueError('Unknown acquisition policy')
        if any(not math.isfinite(v) or v < 0 for v in
               (self.initial_cash_usd,self.monthly_contribution_usd)):
            raise ValueError('Funding must be finite and non-negative')
        if self.max_live_accounts < 1 or not 1 <= self.replacement_target <= self.max_live_accounts:
            raise ValueError('Invalid live-account limits')
        if not 0 <= self.reinvest_fraction <= 1:
            raise ValueError('Reinvestment fraction must be between zero and one')
        if self.evaluation is None and self.evaluations_at_once:
            raise ValueError('Evaluations at once needs an evaluation spec')
        if self.spare_capacity is None:
            if self.passes_per_month or self.evaluation is not None:
                raise ValueError('Limited supply needs a spare shelf; set spare_capacity (0 for none)')
        elif not 0 <= self.spare_capacity < self.max_live_accounts:
            raise ValueError('Spare shelf needs 0 <= spares < live cap')
        elif self.evaluation is None and self.passes_per_month < 1:
            raise ValueError('A pass-rate shelf needs at least one pass a month')
        elif self.evaluation is not None and (self.passes_per_month or self.evaluations_at_once < 1):
            raise ValueError('Evaluation supply needs at least one evaluation at once and no pass rate')


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
    # Accounts the last decision wanted but could not put live.
    shortfall: int = 0
    evaluations: list = field(default_factory=list)
    active: list = field(default_factory=list)
    waiting: dict = field(default_factory=dict)
    settled: int = 0
    router: Router | None = None
    commission_per_mnq: float = 0
    path_order: str = 'mae_first'
    evaluation_fees_usd: float = 0
    activation_fees_usd: float = 0
    pending_month_orders: list = field(default_factory=list)
    last_evaluation_start: datetime | None = None
    pipeline_daily: list = field(default_factory=list)
    financing_events: list = field(default_factory=list)

    @property
    def shelved(self):
        return self.policy.spare_capacity is not None

    @property
    def evaluating(self):
        return self.policy.evaluation is not None

    def cash_event(self, at, kind, amount):
        self.cash_usd = money(self.cash_usd + amount)
        if self.cash_usd < 0:
            raise ValueError('Owner cash became negative')
        self.cash_events.append({'at':at.isoformat(),'kind':kind,'amount_usd':amount,
                                 'cash_after_usd':self.cash_usd})

    def pay(self, at, kind, amount):
        self.spent_usd=money(self.spent_usd+amount)
        self.cash_event(at,kind,-amount)

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
        if self.evaluating: return min(room,self.spares)
        if not self.shelved: return min(room,int(self.cash_usd//fee))
        fresh=min(self.passes_left(at),max(0,room-self.spares),int(self.cash_usd//fee))
        return min(room,self.spares+fresh)

    def limits(self, at, alive, fee, wanted, count):
        room=max(0,self.policy.max_live_accounts-alive)
        short=count<min(wanted,room)
        flags={'capacity_limited':min(wanted,room)<wanted,'cash_limited':short}
        if self.evaluating:
            # A passed account awaiting an unaffordable activation is a cash blockage.
            passed=sum(e.state=='passed' for e in self.active)
            flags.update(cash_limited=short and passed>0,
                         supply_limited=short and self.spares+passed<min(wanted,room))
        elif self.shelved:
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
            self.pay(at,'account_purchase',amount)
        return amount

    def restock(self, at, alive, fee):
        """Pass evaluations to refill the shelf, within this month's passes, the cap and cash."""
        if not self.shelved or self.evaluating: return 0
        room=self.policy.max_live_accounts-alive-self.spares
        n=max(0,min(self.policy.spare_capacity-self.spares,self.passes_left(at),room,int(self.cash_usd//fee)))
        if n:
            self.spares+=n
            self.passes_this_month+=n
            self.pay(at,'spare_purchase',money(n*fee))
            self.spare_events.append({'at':at.isoformat(),'shelved':n,'spares_after':self.spares})
        return n

    # ------------------------------------------------------------ evaluations

    def attach_tape(self, trades, *, commission_per_mnq, path_order):
        self.router=Router(trades)
        self.commission_per_mnq,self.path_order=commission_per_mnq,path_order

    def route(self, evaluation, after):
        index=self.router.first(after,self.settled)
        if index is not None:
            self.waiting.setdefault(index,[]).append((evaluation,evaluation.generation))

    def settle(self, index, trade):
        """Settle one tape trade for every evaluation positioned in it."""
        self.settled=index+1
        for evaluation,generation in self.waiting.pop(index,()):
            if evaluation.state!='running' or evaluation.generation!=generation: continue
            if evaluation.apply(trade,self.policy.evaluation,commission_per_mnq=self.commission_per_mnq,
                                path_order=self.path_order)=='running':
                self.route(evaluation,trade.exit_at)

    def activate(self, at, alive):
        """Activate evaluations that passed since the last check; they join the shelf."""
        fee=self.policy.evaluation.activation_fee_usd
        for e in self.active:
            if e.state!='passed': continue
            if alive+self.spares>=self.policy.max_live_accounts:
                if self.policy.activate_on_first_check:
                    e.state,e.ended_at='cancelled',at
                    self.financing_events.append({'at':at.isoformat(),'kind':'pass_forfeited_capacity','eval_id':e.eval_id})
                    continue
                break
            if self.cash_usd<fee:
                self.financing_events.append({'at':at.isoformat(),'kind':'activation_blocked','eval_id':e.eval_id})
                if self.policy.activate_on_first_check:
                    e.state,e.ended_at='cancelled',at
                    self.financing_events.append({'at':at.isoformat(),'kind':'pass_forfeited_cash','eval_id':e.eval_id})
            else:
                self.pay(at,'activation_fee',fee)
                self.activation_fees_usd=money(self.activation_fees_usd+fee)
                e.state,e.ended_at='funded',at
                self.spares+=1
                self.spare_events.append({'at':at.isoformat(),'shelved':1,'spares_after':self.spares})
        self.active=[e for e in self.active if e.state in IN_FLIGHT]

    def run_evaluations(self, at, alive):
        """Renew, cancel and start evaluations so that those in flight cover what is short."""
        p,spec=self.policy,self.policy.evaluation
        need=self.shortfall+max(0,p.spare_capacity-self.spares)
        due=sorted((e for e in self.active if e.state in ('running','blown') and e.renews_at<=at),
                   key=lambda e:(e.state!='running',e.eval_id))
        keep=need-(len(self.active)-len(due))
        for e in due:
            if keep>0 and self.cash_usd>=spec.monthly_fee_usd:
                self.pay(at,'evaluation_fee',spec.monthly_fee_usd)
                self.evaluation_fees_usd=money(self.evaluation_fees_usd+spec.monthly_fee_usd)
                e.months_paid+=1
                keep-=1
                if e.state=='blown':
                    e.reset(spec)
                    e.resets+=1
                    self.route(e,at)
            else:
                if keep>0:
                    self.financing_events.append({'at':at.isoformat(),'kind':'renewal_unaffordable','eval_id':e.eval_id})
                e.state,e.ended_at='cancelled',at
        self.active=[e for e in self.active if e.state in IN_FLIGHT]
        subscriptions=sum(e.state in ('running','blown') for e in self.active)
        seats=(p.max_live_accounts-alive-self.spares-len(self.active)
               if p.evaluations_reserve_seats else p.evaluations_at_once)
        new=min(p.evaluations_at_once-subscriptions,need-len(self.active),seats)
        if p.evaluation_start_interval_days:
            ready=(self.last_evaluation_start is None or
                   (at-self.last_evaluation_start).days>=p.evaluation_start_interval_days)
            new=min(new,int(ready))
        affordable=int(self.cash_usd//spec.monthly_fee_usd)
        if new>affordable:
            self.financing_events.append({'at':at.isoformat(),'kind':'start_unaffordable','count':new-affordable})
        new=min(new,affordable)
        for _ in range(max(0,new)):
            e=Evaluation(len(self.evaluations)+1,at,months_paid=1)
            e.reset(spec)
            self.pay(at,'evaluation_fee',spec.monthly_fee_usd)
            self.evaluation_fees_usd=money(self.evaluation_fees_usd+spec.monthly_fee_usd)
            self.evaluations.append(e)
            self.active.append(e)
            self.route(e,at)
            self.last_evaluation_start=at
        occupied=alive+self.spares+(len(self.active) if p.evaluations_reserve_seats else 0)
        if occupied>p.max_live_accounts:
            raise ValueError('Live accounts, spares and evaluations exceed the seat cap')

    # -------------------------------------------------------------- decisions

    def decide(self, at, month_index, alive, account_count, fee):
        if fee <= 0: raise ValueError('Cash purchase study requires a positive fee')
        if self.evaluating: self.activate(at,alive)
        if self.policy.persistent_demand:
            count=self.decide_persistent(at,alive,account_count,fee)
        elif self.policy.name in HYBRID:
            count=self.decide_hybrid(at, alive, account_count, fee)
        else:
            count=self.decide_scheduled(at, month_index, alive, fee)
        if self.evaluating:
            self.run_evaluations(at, alive+count)
            self.pipeline_daily.append({'at':at.isoformat(),'alive':alive+count,'spares':self.spares,
                'subscriptions':sum(e.state in ('running','blown') for e in self.active),
                'awaiting_activation':sum(e.state=='passed' for e in self.active),
                'in_flight':len(self.active),'shortfall':self.shortfall,
                'pending_replacements':self.pending_replacements,'cash_usd':self.cash_usd})
        else: self.restock(at, alive+count, fee)
        return count

    def decide_persistent(self, at, alive, account_count, fee):
        """FIFO monthly growth orders persist; deaths first, consuming the current slot.

        Growth orders are admitted only while the live book plus outstanding orders
        is below the live cap. No retrospective orders accumulate while full.
        A replacement consumes this month's order, not an older overdue order.
        """
        deaths=account_count-alive
        self.pending_replacements+=deaths-self.observed_deaths
        self.observed_deaths=deaths
        month=(at.year,at.month)
        if (at.day==1 and month not in self.filled_month_slots
                and alive+self.pending_replacements+len(self.pending_month_orders)<self.policy.max_live_accounts):
            self.pending_month_orders.append(month)
        available=self.obtainable(at,alive,fee)
        replaced=min(self.pending_replacements,available)
        self.pending_replacements-=replaced
        consumed=replaced>0 and month not in self.filled_month_slots
        if consumed:
            self.filled_month_slots.add(month)
            if month in self.pending_month_orders: self.pending_month_orders.remove(month)
        scheduled=min(len(self.pending_month_orders),available-replaced)
        for _ in range(scheduled):
            self.filled_month_slots.add(self.pending_month_orders.pop(0))
        count=replaced+scheduled
        self.shortfall=min(self.pending_replacements+len(self.pending_month_orders),
                           self.policy.max_live_accounts-alive-count)
        self.replacement_events.append({'at':at.isoformat(),'replacements':replaced,
            'scheduled_bought':scheduled,'consumed_current_month_slot':bool(consumed),
            'scheduled_skipped_for_debt':False,'pending_replacements':self.pending_replacements,
            'pending_month_orders':len(self.pending_month_orders),'future_slots_used':0})
        wanted=count+self.shortfall
        if wanted:
            self.decisions.append({'at':at.isoformat(),'wanted':wanted,'bought':count,
                **self.limits(at,alive,fee,wanted,count),'alive_before':alive})
        if count: self.deploy(at,count,fee)
        return count

    def decide_scheduled(self, at, month_index, alive, fee):
        p=self.policy
        room=max(0,p.max_live_accounts-alive)
        wanted=0
        self.shortfall=0
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
        self.shortfall=min(wanted,room)-count
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
        self.shortfall = max(0,min(wanted,self.policy.max_live_accounts-alive)-count)
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
        if self.evaluating:
            evs=self.evaluations
            out.update(evaluations_started=len(evs),
                       evaluation_months_paid=sum(e.months_paid for e in evs),
                       evaluation_resets=sum(e.resets for e in evs),
                       evaluations_passed=sum(e.passed_at is not None for e in evs),
                       evaluations_activated=sum(e.state=='funded' for e in evs),
                       evaluations_cancelled=sum(e.state=='cancelled' for e in evs),
                       evaluations_in_flight_at_end=len(self.active),
                       evaluation_fees_usd=self.evaluation_fees_usd,
                       activation_fees_usd=self.activation_fees_usd)
        return out
