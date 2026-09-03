"""Shared fixtures. The tape and both brick arms are loaded once per test run."""

from __future__ import annotations

from pa_milky.config import PROJECT_ROOT, load_config
from pa_milky.loader import load_trades
from pa_milky.simulator import run_book

BRICK1_CONFIG_PATH = PROJECT_ROOT / "config" / "bricks" / "brick1_ideal_world.json"
BRICK2_CONFIG_PATH = PROJECT_ROOT / "config" / "bricks" / "brick2_monthly_100.json"

BRICK1 = load_config(BRICK1_CONFIG_PATH)
BRICK2 = load_config(BRICK2_CONFIG_PATH)

TRADES = load_trades(
    BRICK1.sweeps_root, strategy=BRICK1.strategy, risk_reward=BRICK1.risk_reward
)

RESULT1 = run_book(TRADES, BRICK1)
RESULT2 = run_book(TRADES, BRICK2)
