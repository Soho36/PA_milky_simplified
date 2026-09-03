"""Command line entry point for the brick-1 simulator."""

from __future__ import annotations

import argparse
import dataclasses
from datetime import datetime
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH, PROJECT_ROOT, load_config
from .loader import load_trades
from .report import render_text, write_outputs
from .simulator import run_book


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pa_milky",
        description="Ideal-world Legacy 25K PA book: one new account per month.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--strategy", help="override the configured strategy (RR or GG)")
    parser.add_argument("--rr", help="override the configured risk/reward, e.g. 1.00")
    parser.add_argument(
        "--commission",
        type=float,
        help="override the round-turn commission per MNQ",
    )
    parser.add_argument(
        "--path-order",
        choices=("mae_first", "mfe_first"),
        help="override how a trade that touches both extremes is resolved",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="directory for summary.json, accounts.csv and report.txt "
        "(default: results/<timestamp>_<strategy>_rr<rr>)",
    )
    parser.add_argument("--no-write", action="store_true", help="print only, write nothing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)

    overrides = {}
    if args.strategy:
        overrides["strategy"] = args.strategy
    if args.rr:
        overrides["risk_reward"] = args.rr
    if args.commission is not None:
        overrides["commission_usd_per_mnq_round_turn"] = args.commission
    if args.path_order:
        overrides["path_order"] = args.path_order
    if overrides:
        config = dataclasses.replace(config, **overrides)

    trades = load_trades(
        config.sweeps_root, strategy=config.strategy, risk_reward=config.risk_reward
    )
    result = run_book(trades, config)
    print(render_text(result))

    if not args.no_write:
        out = args.out
        if out is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"{stamp}_{config.strategy}_rr{config.risk_reward}"
            out = PROJECT_ROOT / "results" / name
        written = write_outputs(result, out)
        print()
        for label, path in written.items():
            print(f"  wrote {label}: {path}")
    return 0
