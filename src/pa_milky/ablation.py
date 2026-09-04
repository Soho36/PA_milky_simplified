"""What each firm rule is worth, measured by switching it off.

The brick ladder could only ever give marginal effects in the order rules
happened to be added. Ablation gives each rule's own price against the full
rulebook: run everything on, then everything-minus-one, and read the deltas.

A rule with a positive delta costs us money. A rule with a negative delta is
worth more to us than it takes -- which is not a hypothetical: the safety net
stops us paying an account down to the edge of its own liquidation.
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
    gross_usd: float
    alive: int
    payouts: int
    denials: int

    @classmethod
    def measure(cls, label: str, rule: str | None, trades: list[Trade], config: RunConfig) -> "Arm":
        result = run_book(trades, config)
        return cls(
            label=label,
            rule=rule,
            pocket_usd=result.pocket_usd,
            gross_usd=result.total_withdrawn_usd,
            alive=len(result.alive),
            payouts=len(result.payouts),
            denials=len(result.denials),
        )


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
    add("=" * 78)
    add("  ABLATION - what each firm rule is worth")
    add("=" * 78)
    add("  Each row switches off exactly one rule and re-runs the whole tape.")
    add("  A positive delta is what that rule costs us; a negative delta means")
    add("  the rule protects more than it takes.")
    add("")
    add(f"  {'arm':<28}{'pocket':>13}{'delta':>13}{'alive':>7}{'payouts':>9}{'denied':>8}")
    add("  " + "-" * 76)
    add(
        f"  {baseline.label:<28}{baseline.pocket_usd:>13,.0f}{'-':>13}"
        f"{baseline.alive:>7}{baseline.payouts:>9}{baseline.denials:>8}"
    )
    for arm in arms:
        delta = arm.pocket_usd - baseline.pocket_usd
        add(
            f"  {arm.label:<28}{arm.pocket_usd:>13,.0f}{delta:>+13,.0f}"
            f"{arm.alive:>7}{arm.payouts:>9}{arm.denials:>8}"
        )
    add("=" * 78)
    return "\n".join(lines)


def ablation_payload(baseline: Arm, arms: list[Arm]) -> dict:
    return {
        "baseline": dataclasses.asdict(baseline),
        "arms": [
            {**dataclasses.asdict(arm), "delta_pocket_usd": round(arm.pocket_usd - baseline.pocket_usd, 2)}
            for arm in arms
        ],
    }
