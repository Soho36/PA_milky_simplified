"""Typed view over a brick's runtime configuration.

A config round-trips through a plain JSON payload in both directions, so a
sealed baseline can carry its own complete config and be re-run years later
without depending on whatever ``config/runtime.json`` happens to say today.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "runtime.json"
SCHEMA_VERSION = "pa_milky_simplified.runtime.v1"

WITHDRAWAL_POLICIES = ("none", "fixed_monthly")
SHORTFALL_RULES = ("skip", "accrue_backlog", "partial")


@dataclass(frozen=True, slots=True)
class WithdrawalRules:
    """How cash leaves an account. ``none`` reproduces brick 1."""

    policy: str = "none"
    amount_usd: float = 0.0
    # Balance an account must show at the decision before any cash may leave.
    eligibility_balance_usd: float = 0.0
    # Balance a withdrawal may not cut into. None removes the amount cap.
    safety_net_balance_usd: float | None = None
    shortfall: str = "skip"

    def __post_init__(self) -> None:
        if self.policy not in WITHDRAWAL_POLICIES:
            raise ValueError(f"Unknown withdrawal policy: {self.policy!r}")
        if self.shortfall not in SHORTFALL_RULES:
            raise ValueError(f"Unknown shortfall rule: {self.shortfall!r}")
        if self.policy != "none" and self.amount_usd <= 0:
            raise ValueError("A withdrawal policy needs a positive amount")

    @property
    def enabled(self) -> bool:
        return self.policy != "none"


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
    # withdrawals
    withdrawals: WithdrawalRules
    # labelling
    brick: int = 1
    brick_name: str = "unnamed"

    @property
    def commission_per_copy_usd(self) -> float:
        return self.commission_usd_per_mnq_round_turn * self.contracts_per_copy


def config_from_payload(payload: dict) -> RunConfig:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported runtime schema: {payload.get('schema_version')!r}")
    data, execution = payload["data"], payload["execution"]
    account, book = payload["account"], payload["book"]
    # Brick 1 predates withdrawals, so a payload without the block is valid and
    # means "no cash ever leaves an account".
    withdrawals = payload.get("withdrawals", {"policy": "none"})

    if execution["path_order"] not in {"mae_first", "mfe_first"}:
        raise ValueError(f"Unknown path_order: {execution['path_order']!r}")
    if execution["concurrency"] != "unlimited":
        raise ValueError("Unlimited concurrency is the only modelled exposure rule")

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
        withdrawals=WithdrawalRules(
            policy=withdrawals.get("policy", "none"),
            amount_usd=float(withdrawals.get("amount_usd", 0.0)),
            eligibility_balance_usd=float(withdrawals.get("eligibility_balance_usd", 0.0)),
            safety_net_balance_usd=(
                None
                if withdrawals.get("safety_net_balance_usd") is None
                else float(withdrawals["safety_net_balance_usd"])
            ),
            shortfall=withdrawals.get("shortfall", "skip"),
        ),
        brick=int(payload.get("brick", 1)),
        brick_name=payload.get("brick_name", "unnamed"),
    )


def to_payload(config: RunConfig) -> dict:
    """Rebuild the JSON form, including any command line overrides."""

    try:
        sweeps_root = config.sweeps_root.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        sweeps_root = config.sweeps_root.as_posix()

    return {
        "schema_version": SCHEMA_VERSION,
        "brick": config.brick,
        "brick_name": config.brick_name,
        "data": {
            "sweeps_root": sweeps_root,
            "strategy": config.strategy,
            "risk_reward": config.risk_reward,
            "expected_windows": config.expected_windows,
            "expected_trades": config.expected_trades,
        },
        "execution": {
            "contracts_per_copy": config.contracts_per_copy,
            "commission_usd_per_mnq_round_turn": config.commission_usd_per_mnq_round_turn,
            "slippage_ticks": 0,
            "concurrency": config.concurrency,
            "path_order": config.path_order,
            "commission_applies_to_excursions": False,
        },
        "account": {
            "starting_balance_usd": config.starting_balance_usd,
            "trailing_drawdown_usd": config.trailing_drawdown_usd,
            "frozen_floor_profit_usd": config.frozen_floor_profit_usd,
            "threshold_touch_fails": config.threshold_touch_fails,
            "purchase_fee_usd": config.purchase_fee_usd,
        },
        "book": {
            "cadence": "one_new_pa_per_calendar_month",
            "activation_moment": "first_instant_of_calendar_month",
            "max_accounts": config.max_accounts,
            "replace_on_death": config.replace_on_death,
        },
        "withdrawals": {
            "policy": config.withdrawals.policy,
            "amount_usd": config.withdrawals.amount_usd,
            "eligibility_balance_usd": config.withdrawals.eligibility_balance_usd,
            "safety_net_balance_usd": config.withdrawals.safety_net_balance_usd,
            "shortfall": config.withdrawals.shortfall,
        },
    }


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> RunConfig:
    return config_from_payload(json.loads(Path(path).read_text(encoding="utf-8")))
