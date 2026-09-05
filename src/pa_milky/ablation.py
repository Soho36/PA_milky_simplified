"""What each firm rule costs, measured two ways.

A rule can be measured against a *fixed* policy or against an *adapted* one,
and the two answer different questions:

- **Fixed-policy effect.** Remove the rule, change nothing else. This explains
  the arm you are actually running: why this policy earns what it earns.
- **Adapted-policy effect.** Search the same policy choices with and without
  the rule and compare the two best outcomes. This is how much the restriction
  narrows what is achievable, which is the question a trader is really asking.

They can disagree completely. The safety net has a large fixed-policy effect
against a policy with no cushion of its own, and none at all once the policy is
allowed to adapt.

The adapted number is a **lower bound on a rule's cost, and only as good as the
search**. Removing a constraint cannot really narrow what is achievable, so a
negative delta is always a search failure rather than a finding: either the
grid is too coarse to follow the optimum as it moves, or the policy space
cannot imitate what the rule was doing. Both happen here. Treat a negative
delta as "refine the grid", not as "the rule helped us".

A pocket delta on its own also conflates three different things, so every arm
reports the value decomposition too:

- **pocket** -- cash actually taken.
- **stranded** -- equity still standing in live accounts at the horizon.
- **value = pocket + stranded** -- everything the book was worth.

If a rule moves pocket but leaves value unchanged, it blocked *access*: the
money is still in the account. If it moves value, it changed which accounts
survived, and that money was never earned at all. Denial counts cannot tell
these apart, and neither can withheld counts -- fewer denials often just means
our own policy stopped asking.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from .config import RunConfig
from .loader import Trade
from .simulator import run_book


@dataclass(frozen=True, slots=True)
class Arm:
    label: str
    rule: str | None
    pocket_usd: float
    stranded_usd: float
    value_usd: float
    alive: int
    payouts: int
    denials: int
    withheld: int
    fates: tuple[tuple[int, str], ...]

    @classmethod
    def measure(
        cls, label: str, rule: str | None, trades: list[Trade], config: RunConfig
    ) -> "Arm":
        result = run_book(trades, config)
        stranded = result.equity_at_horizon_usd
        return cls(
            label=label,
            rule=rule,
            pocket_usd=result.pocket_usd,
            stranded_usd=stranded,
            value_usd=round(result.pocket_usd + stranded, 2),
            alive=result.alive_at_horizon,
            payouts=len(result.payouts),
            denials=len(result.denials),
            withheld=sum(a.requests_withheld for a in result.accounts),
            fates=tuple(
                (a.account_id, a.died_at.isoformat() if a.died_at else "alive")
                for a in result.accounts
            ),
        )

    def fates_changed_against(self, other: "Arm") -> int:
        return sum(1 for mine, theirs in zip(self.fates, other.fates) if mine != theirs)


# ------------------------------------------------------------- fixed policy


def run_ablation(trades: list[Trade], config: RunConfig) -> tuple[Arm, list[Arm]]:
    """The full rulebook, then one arm per active rule with that rule off."""

    baseline = Arm.measure("all rules on", None, trades, config)
    arms = []
    for key in config.rulebook.active_keys:
        ablated = dataclasses.replace(config, rulebook=config.rulebook.without(key))
        arms.append(Arm.measure(f"minus {key}", key, trades, ablated))
    arms.sort(key=lambda arm: arm.pocket_usd - baseline.pocket_usd, reverse=True)
    return baseline, arms


def render_ablation(baseline: Arm, arms: list[Arm]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=" * 92)
    add("  FIXED-POLICY ABLATION - each rule off, our behaviour unchanged")
    add("=" * 92)
    add("  d.pocket  cash gained by removing the rule")
    add("  d.value   pocket + equity still standing; a change here means accounts")
    add("            lived or died differently, so the money was never earned")
    add("  fates     accounts whose death outcome moved")
    add("")
    add(
        f"  {'arm':<26}{'pocket':>11}{'d.pocket':>11}{'d.value':>11}"
        f"{'alive':>7}{'fates':>7}{'payouts':>9}{'denied':>8}{'withheld':>10}"
    )
    add("  " + "-" * 90)
    add(
        f"  {baseline.label:<26}{baseline.pocket_usd:>11,.0f}{'-':>11}{'-':>11}"
        f"{baseline.alive:>7}{'-':>7}{baseline.payouts:>9}"
        f"{baseline.denials:>8}{baseline.withheld:>10}"
    )
    for arm in arms:
        add(
            f"  {arm.label:<26}{arm.pocket_usd:>11,.0f}"
            f"{arm.pocket_usd - baseline.pocket_usd:>+11,.0f}"
            f"{arm.value_usd - baseline.value_usd:>+11,.0f}"
            f"{arm.alive:>7}{arm.fates_changed_against(baseline):>7}"
            f"{arm.payouts:>9}{arm.denials:>8}{arm.withheld:>10}"
        )
    add("=" * 92)
    return "\n".join(lines)


# ----------------------------------------------------------- adapted policy


def cushion_grid(config: RunConfig, span_usd: float = 10_000.0, step_usd: float = 500.0):
    """Retained-balance levels, expressed as headroom above the frozen floor."""

    floor = config.trailing_floor_balance_usd
    levels: list[float | None] = [None]
    steps = int(span_usd // step_usd) + 1
    levels += [round(floor + step_usd * i, 2) for i in range(steps)]
    return levels


def best_over_cushions(
    trades: list[Trade], config: RunConfig, levels: list[float | None]
) -> tuple[float, float | None]:
    """The best pocket this rulebook can reach, and the cushion that reached it."""

    best_pocket = float("-inf")
    best_level: float | None = None
    for level in levels:
        arm = dataclasses.replace(
            config,
            policy=dataclasses.replace(config.policy, min_retained_balance_usd=level),
        )
        pocket = run_book(trades, arm).pocket_usd
        if pocket > best_pocket:
            best_pocket, best_level = pocket, level
    return round(best_pocket, 2), best_level


def run_adapted_ablation(
    trades: list[Trade], config: RunConfig, levels: list[float | None] | None = None
) -> dict:
    """Optimise the cushion with and without each rule, then compare the bests."""

    levels = cushion_grid(config) if levels is None else levels
    floor = config.trailing_floor_balance_usd
    base_pocket, base_level = best_over_cushions(trades, config, levels)
    rows = []
    for key in config.rulebook.active_keys:
        ablated = dataclasses.replace(config, rulebook=config.rulebook.without(key))
        pocket, level = best_over_cushions(trades, ablated, levels)
        rows.append(
            {
                "rule": key,
                "best_pocket_usd": pocket,
                "best_cushion_usd": level,
                "best_headroom_usd": None if level is None else round(level - floor, 2),
                "delta_vs_best_usd": round(pocket - base_pocket, 2),
            }
        )
    rows.sort(key=lambda row: row["delta_vs_best_usd"], reverse=True)
    return {
        "search": {
            "lever": "min_retained_balance_usd",
            "levels": len(levels),
            "floor_balance_usd": floor,
        },
        "baseline": {
            "best_pocket_usd": base_pocket,
            "best_cushion_usd": base_level,
            "best_headroom_usd": None if base_level is None else round(base_level - floor, 2),
        },
        "arms": rows,
    }


def render_adapted(payload: dict) -> str:
    base = payload["baseline"]
    lines: list[str] = []
    add = lines.append
    add("=" * 92)
    add("  ADAPTED-POLICY ABLATION - best achievable with the rule, and without it")
    add("=" * 92)
    add(
        f"  The cushion is re-optimised for every arm over {payload['search']['levels']}"
        " levels. A delta here"
    )
    add("  is how much the rule narrows what is achievable, not what it costs the")
    add("  policy we happen to run. Headroom is measured above the frozen floor at")
    add(f"  ${payload['search']['floor_balance_usd']:,.0f}.")
    add("")
    add(f"  {'arm':<26}{'best pocket':>14}{'delta':>13}{'best headroom':>16}")
    add("  " + "-" * 70)
    head = "none" if base["best_headroom_usd"] is None else f"{base['best_headroom_usd']:,.0f}"
    add(f"  {'all rules on':<26}{base['best_pocket_usd']:>14,.0f}{'-':>13}{head:>16}")
    for row in payload["arms"]:
        head = "none" if row["best_headroom_usd"] is None else f"{row['best_headroom_usd']:,.0f}"
        add(
            f"  {'minus ' + row['rule']:<26}{row['best_pocket_usd']:>14,.0f}"
            f"{row['delta_vs_best_usd']:>+13,.0f}{head:>16}"
        )
    add("=" * 92)
    return "\n".join(lines)


def ablation_payload(baseline: Arm, arms: list[Arm]) -> dict:
    def row(arm: Arm) -> dict:
        return {
            "label": arm.label,
            "rule": arm.rule,
            "pocket_usd": arm.pocket_usd,
            "stranded_usd": arm.stranded_usd,
            "value_usd": arm.value_usd,
            "alive": arm.alive,
            "payouts": arm.payouts,
            "denials": arm.denials,
            "withheld": arm.withheld,
        }

    return {
        "baseline": row(baseline),
        "arms": [
            {
                **row(arm),
                "delta_pocket_usd": round(arm.pocket_usd - baseline.pocket_usd, 2),
                "delta_value_usd": round(arm.value_usd - baseline.value_usd, 2),
                "fates_changed": arm.fates_changed_against(baseline),
            }
            for arm in arms
        ],
    }
