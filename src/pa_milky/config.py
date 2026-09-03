"""Typed view over config/runtime.json."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "runtime.json"
SCHEMA_VERSION = "pa_milky_simplified.runtime.v1"


@dataclass(frozen=True, slots=True)
class RunConfig:
    # data
    sweeps_root: Path
    strategy: str
    risk_reward: str
    expected_windows: int
    expected_trades: int
    # execution
    contracts_per_copy: int
    commission_usd_per_mnq_round_turn: float
    path_order: str
    concurrency: str
    # account
    starting_balance_usd: float
    trailing_drawdown_usd: float
    frozen_floor_profit_usd: float
    threshold_touch_fails: bool
    purchase_fee_usd: float
    # book
    replace_on_death: bool
    max_accounts: int | None

    @property
    def commission_per_copy_usd(self) -> float:
        return self.commission_usd_per_mnq_round_turn * self.contracts_per_copy


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> RunConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported runtime schema: {payload.get('schema_version')!r}")
    data, execution = payload["data"], payload["execution"]
    account, book = payload["account"], payload["book"]

    if execution["path_order"] not in {"mae_first", "mfe_first"}:
        raise ValueError(f"Unknown path_order: {execution['path_order']!r}")
    if execution["concurrency"] != "unlimited":
        raise ValueError("Brick 1 models unlimited concurrency only")

    root = Path(data["sweeps_root"])
    if not root.is_absolute():
        root = PROJECT_ROOT / root
    return RunConfig(
        sweeps_root=root,
        strategy=data["strategy"],
        risk_reward=data["risk_reward"],
        expected_windows=int(data["expected_windows"]),
        expected_trades=int(data["expected_trades"]),
        contracts_per_copy=int(execution["contracts_per_copy"]),
        commission_usd_per_mnq_round_turn=float(
            execution["commission_usd_per_mnq_round_turn"]
        ),
        path_order=execution["path_order"],
        concurrency=execution["concurrency"],
        starting_balance_usd=float(account["starting_balance_usd"]),
        trailing_drawdown_usd=float(account["trailing_drawdown_usd"]),
        frozen_floor_profit_usd=float(account["frozen_floor_profit_usd"]),
        threshold_touch_fails=bool(account["threshold_touch_fails"]),
        purchase_fee_usd=float(account["purchase_fee_usd"]),
        replace_on_death=bool(book["replace_on_death"]),
        max_accounts=book["max_accounts"],
    )
