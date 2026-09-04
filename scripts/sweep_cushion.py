"""Sweep our own retained-cushion level with the firm's rulebook switched on.

The cushion is the one lever that is entirely ours: how much balance we refuse
to take out of an account, whatever the rules would allow. Too low and we strip
accounts to the edge of liquidation and they stop paying; too high and we leave
money in accounts that die holding it.

Usage:
    python scripts/sweep_cushion.py [--policy monthly_500|monthly_maximum] [--fine]
"""

from __future__ import annotations

import argparse
import dataclasses
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pa_milky.config import CONFIG_ROOT, load_config  # noqa: E402
from pa_milky.loader import load_trades  # noqa: E402
from pa_milky.simulator import run_book  # noqa: E402

SCENARIOS = {
    "monthly_500": "full_rulebook_monthly_500.json",
    "monthly_maximum": "full_rulebook_monthly_maximum.json",
}


def sweep(policy: str, levels: list[float | None], strategy: str | None = None) -> list[dict]:
    config = load_config(CONFIG_ROOT / "scenarios" / SCENARIOS[policy])
    if strategy:
        config = dataclasses.replace(config, strategy=strategy)
    trades = load_trades(
        config.sweeps_root, strategy=config.strategy, risk_reward=config.risk_reward
    )
    rows = []
    for level in levels:
        arm = dataclasses.replace(
            config,
            policy=dataclasses.replace(config.policy, min_retained_balance_usd=level),
        )
        result = run_book(trades, arm)
        rows.append(
            {
                "cushion_usd": level,
                "pocket_usd": result.pocket_usd,
                "gross_usd": result.total_withdrawn_usd,
                "alive": len(result.alive),
                "payouts": len(result.payouts),
                "denials": len(result.denials),
                "equity_left_usd": round(
                    sum(a.balance_usd for a in result.alive), 2
                ),
            }
        )
    return rows


def render(policy: str, rows: list[dict]) -> str:
    best = max(rows, key=lambda row: row["pocket_usd"])
    lines = [
        "=" * 72,
        f"  CUSHION SWEEP - full rulebook on, policy {policy}",
        "=" * 72,
        f"  {'cushion':>10}{'pocket':>12}{'gross':>12}{'alive':>7}"
        f"{'payouts':>9}{'left in accts':>15}",
        "  " + "-" * 65,
    ]
    for row in rows:
        label = "none" if row["cushion_usd"] is None else f"{row['cushion_usd']:,.0f}"
        mark = "  <-- best" if row is best else ""
        lines.append(
            f"  {label:>10}{row['pocket_usd']:>12,.0f}{row['gross_usd']:>12,.0f}"
            f"{row['alive']:>7}{row['payouts']:>9}{row['equity_left_usd']:>15,.0f}{mark}"
        )
    lines.append("=" * 72)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=sorted(SCENARIOS), default="monthly_500")
    parser.add_argument("--from", dest="start", type=float)
    parser.add_argument("--to", dest="stop", type=float)
    parser.add_argument("--step", type=float, default=100.0)
    parser.add_argument("--strategy", help="override the tape, e.g. GG")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    if args.start is not None and args.stop is not None:
        levels: list[float | None] = []
        value = args.start
        while value <= args.stop + 1e-9:
            levels.append(round(value, 2))
            value += args.step
    else:
        levels = [None] + [25_000.0 + 500.0 * i for i in range(1, 21)]

    rows = sweep(args.policy, levels, args.strategy)
    label = f"{args.policy} on {args.strategy or 'RR'}"
    print(render(label, rows))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps({"policy": args.policy, "rows": rows}, indent=2), encoding="utf-8"
        )
        print(f"\n  wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
