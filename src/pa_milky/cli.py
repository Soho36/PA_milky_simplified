"""Command line entry point."""

from __future__ import annotations

import argparse
import dataclasses
import json
from datetime import datetime
from pathlib import Path

from .ablation import (
    ablation_payload,
    render_ablation,
    render_adapted,
    run_ablation,
    run_adapted_ablation,
)
from .config import DEFAULT_CONFIG_PATH, PROJECT_ROOT, load_config
from .loader import load_tape
from .provenance import list_baselines, seal, verify
from .report import render_text, summarize, write_outputs
from .simulator import run_book


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pa_milky",
        description="Legacy 25K PA book simulator, built one rule at a time.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--strategy", help="override the configured strategy (RR or GG)")
    parser.add_argument("--rr", help="override the configured risk/reward, e.g. 1.00")
    parser.add_argument(
        "--commission", type=float, help="override the round-turn commission per MNQ"
    )
    parser.add_argument(
        "--path-order",
        choices=("mae_first", "mfe_first"),
        help="override how a trade that touches both extremes is resolved",
    )
    parser.add_argument(
        "--withdraw",
        type=float,
        help="override the monthly per-account request amount (0 disables it)",
    )
    parser.add_argument(
        "--rule-off",
        action="append",
        default=[],
        metavar="KEY",
        help="switch one firm rule off; repeatable",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="directory for summary.json, accounts.csv and report.txt "
        "(default: results/<timestamp>_<strategy>_rr<rr>)",
    )
    parser.add_argument("--no-write", action="store_true", help="print only, write nothing")
    parser.add_argument(
        "--ablate",
        action="store_true",
        help="also re-run the tape once per active firm rule with that rule off, "
        "holding our behaviour fixed",
    )
    parser.add_argument(
        "--ablate-adapted",
        action="store_true",
        help="also re-optimise the cushion with and without each rule, and compare "
        "the best achievable outcomes",
    )
    parser.add_argument(
        "--seal",
        metavar="NAME",
        help="also seal this run as baselines/NAME with full provenance",
    )
    parser.add_argument(
        "--verify-baseline",
        metavar="NAME",
        help="re-run a sealed baseline against today's engine and exit",
    )
    parser.add_argument(
        "--verify-all", action="store_true", help="verify every sealed baseline and exit"
    )
    return parser


def _apply_overrides(config, args):
    overrides = {}
    if args.strategy:
        overrides["strategy"] = args.strategy
    if args.rr:
        overrides["risk_reward"] = args.rr
    if args.strategy or args.rr:
        # The declared tape size belongs to the scenario's own strategy. Carry
        # it onto a different tape and it becomes a false claim in the manifest.
        overrides["expected_trades"] = None
        overrides["expected_windows"] = None
        print(
            "  note: tape overridden, so the scenario's declared size no longer "
            "applies and this run is not size-verified"
        )
    if args.commission is not None:
        overrides["commission_usd_per_mnq_round_turn"] = args.commission
    if args.path_order:
        overrides["path_order"] = args.path_order
    if args.withdraw is not None:
        overrides["policy"] = dataclasses.replace(
            config.policy,
            cadence="calendar_month" if args.withdraw > 0 else "never",
            amount_usd=args.withdraw,
            amount_rule="fixed",
        )
    if args.rule_off:
        rulebook = config.rulebook
        for key in args.rule_off:
            rulebook = rulebook.without(key)
        overrides["rulebook"] = rulebook
    return dataclasses.replace(config, **overrides) if overrides else config


def _verify(names: list[str]) -> int:
    if not names:
        print("no sealed baselines found under baselines/")
        return 1
    failed = 0
    for name in names:
        result = verify(name)
        print(result.render())
        failed += 0 if result.ok else 1
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.verify_all:
        return _verify(list_baselines())
    if args.verify_baseline:
        return _verify([args.verify_baseline])

    config = _apply_overrides(load_config(args.config), args)
    trades = load_tape(config)
    result = run_book(trades, config)
    print(render_text(result))

    ablation = None
    if args.ablate or args.ablate_adapted:
        ablation = {}
    if args.ablate:
        baseline, arms = run_ablation(trades, config)
        ablation["fixed_policy"] = ablation_payload(baseline, arms)
        print()
        print(render_ablation(baseline, arms))
    if args.ablate_adapted:
        adapted = run_adapted_ablation(trades, config)
        ablation["adapted_policy"] = adapted
        print()
        print(render_adapted(adapted))

    if args.no_write and args.seal:
        raise SystemExit("--seal needs written outputs; drop --no-write")

    if not args.no_write:
        out = args.out
        if out is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = PROJECT_ROOT / "results" / f"{stamp}_{config.strategy}_rr{config.risk_reward}"
        written = write_outputs(result, out)
        if ablation is not None:
            path = Path(out) / "ablation.json"
            path.write_text(json.dumps(ablation, indent=2), encoding="utf-8")
            written["ablation"] = path
        print()
        for label, path in written.items():
            print(f"  wrote {label}: {path}")
        if args.seal:
            manifest = seal(args.seal, config, summarize(result), Path(out))
            print(f"  sealed baseline: {manifest}")
    return 0
