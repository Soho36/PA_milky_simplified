"""Layered configuration.

Four layers with different lifetimes:

- **product** -- the account specification. Stone. Balance, trailing drawdown,
  where the floor freezes, what a seat costs.
- **firm rules** -- everything Apex imposes on a payout. Switchable, one flag
  and a few parameters each.
- **policy** -- what *we* choose to ask for and how often. Ours, not theirs.
- **scenario** -- a named run that binds the three to a tape.

A scenario may name a layer by file path or inline it, and may override
individual fields of a named layer. Whatever the source, ``to_payload``
emits the fully resolved form, so a sealed baseline is always self-contained
and can never be changed by a later edit to ``config/``.

The older flat ``runtime.v1`` payload is still accepted, because the brick 1
and brick 2 baselines were sealed with it. It is translated onto the same
layers rather than run down a second code path.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .firm import RULE_TYPES, Rulebook
from .policy import WithdrawalPolicy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = PROJECT_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_ROOT / "scenarios" / "full_rulebook_monthly_500.json"

LEGACY_SCHEMA = "pa_milky_simplified.runtime.v1"
SCENARIO_SCHEMA = "pa_milky_simplified.scenario.v1"


@dataclass(frozen=True, slots=True)
class RunConfig:
    # identity
    scenario: str
    description: str
    brick: int | None
    brick_name: str
    # tape
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
    # product: stone
    product_name: str
    starting_balance_usd: float
    trailing_drawdown_usd: float
    frozen_floor_profit_usd: float
    threshold_touch_fails: bool
    purchase_fee_usd: float
    # book
    replace_on_death: bool
    max_accounts: int | None
    # switchable
    rulebook: Rulebook
    policy: WithdrawalPolicy

    @property
    def commission_per_copy_usd(self) -> float:
        return self.commission_usd_per_mnq_round_turn * self.contracts_per_copy

    @property
    def trailing_floor_balance_usd(self) -> float:
        """Where the trailing threshold freezes -- $25,100 for a 25K account."""

        return self.starting_balance_usd + self.frozen_floor_profit_usd

    @property
    def firm_minimum_payout_usd(self) -> float:
        rule = self.rulebook.get("minimum_payout")
        return rule.amount_usd if rule.enabled else 0.0


# ----------------------------------------------------------------- resolution


def _resolve(value, *, what: str) -> dict:
    """A layer is either an inline object or a path under ``config/``."""

    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        path = CONFIG_ROOT / value
        if not path.is_file():
            raise FileNotFoundError(f"{what} layer not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
    raise ValueError(f"{what} must be an object or a path, got {type(value).__name__}")


def _merge(base: dict, overrides: dict) -> dict:
    """One level of nesting is enough for every layer we have."""

    merged = {key: dict(value) if isinstance(value, dict) else value
              for key, value in base.items()}
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def _sweeps_root(raw: str) -> Path:
    root = Path(raw)
    return root if root.is_absolute() else PROJECT_ROOT / root


def _check_execution(execution: dict) -> None:
    if execution["path_order"] not in {"mae_first", "mfe_first"}:
        raise ValueError(f"Unknown path_order: {execution['path_order']!r}")
    if execution["concurrency"] != "unlimited":
        raise ValueError("Unlimited concurrency is the only modelled exposure rule")


def _from_scenario(payload: dict) -> RunConfig:
    data, execution = payload["data"], payload["execution"]
    _check_execution(execution)
    product = _merge(_resolve(payload["product"], what="product"),
                     payload.get("product_overrides", {}))
    firm = _merge(_resolve(payload["firm_rules"], what="firm_rules"),
                  payload.get("firm_rule_overrides", {}))
    policy = _merge(_resolve(payload["policy"], what="policy"),
                    payload.get("policy_overrides", {}))
    book = payload["book"]
    name = payload.get("scenario", "unnamed")

    return RunConfig(
        scenario=name,
        description=payload.get("description", ""),
        brick=payload.get("brick"),
        brick_name=payload.get("brick_name", name),
        sweeps_root=_sweeps_root(data["sweeps_root"]),
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
        product_name=product.get("product", "unnamed"),
        starting_balance_usd=float(product["starting_balance_usd"]),
        trailing_drawdown_usd=float(product["trailing_drawdown_usd"]),
        frozen_floor_profit_usd=float(product["frozen_floor_profit_usd"]),
        threshold_touch_fails=bool(product["threshold_touch_fails"]),
        purchase_fee_usd=float(product["purchase_fee_usd"]),
        replace_on_death=bool(book["replace_on_death"]),
        max_accounts=book["max_accounts"],
        rulebook=Rulebook.from_payload(firm),
        policy=WithdrawalPolicy.from_payload(policy),
    )


def _legacy_rulebook(withdrawals: dict) -> Rulebook:
    """Translate a runtime.v1 withdrawals block onto the rulebook.

    v1 knew two gates: a flat eligibility balance, and a floor a withdrawal
    could not cut into. Those are ``minimum_balance`` and a ``safety_net``
    whose encroachment allowance is the distance between them, applied to
    every payout because v1 had no payout counter.
    """

    off = {key: {"enabled": False} for key in RULE_TYPES}
    off["profit_split"].update(
        {"mode": "cumulative_threshold", "full_rate_threshold_usd": 25_000.0,
         "reduced_rate": 0.9, "full_rate_from_payout": 6}
    )
    off["processing_delay"].update({"days": 0})
    if withdrawals.get("policy", "none") == "none":
        return Rulebook.from_payload(off)

    gate = float(withdrawals.get("eligibility_balance_usd", 0.0))
    if gate > 0:
        off["minimum_balance"] = {"enabled": True, "balance_usd": gate}
    floor = withdrawals.get("safety_net_balance_usd")
    if floor is not None:
        off["safety_net"] = {
            "enabled": True,
            "net_balance_usd": gate,
            "encroachment_allowance_usd": round(gate - float(floor), 2),
            "applies_through_payout": None,
        }
    minimum = withdrawals.get("minimum_request_usd")
    if minimum:
        off["minimum_payout"] = {"enabled": True, "amount_usd": float(minimum)}
    return Rulebook.from_payload(off)


def _from_legacy(payload: dict) -> RunConfig:
    data, execution = payload["data"], payload["execution"]
    _check_execution(execution)
    account, book = payload["account"], payload["book"]
    withdrawals = payload.get("withdrawals", {"policy": "none"})
    enabled = withdrawals.get("policy", "none") != "none"

    policy = WithdrawalPolicy(
        name=payload.get("brick_name", "legacy"),
        cadence="calendar_month" if enabled else "never",
        amount_usd=float(withdrawals.get("amount_usd", 0.0)),
        amount_rule="fixed",
        shortfall=withdrawals.get("shortfall", "skip"),
        quantize_to_amount=True,
    )
    return RunConfig(
        scenario=payload.get("brick_name", "legacy"),
        description=payload.get("description", ""),
        brick=payload.get("brick"),
        brick_name=payload.get("brick_name", "unnamed"),
        sweeps_root=_sweeps_root(data["sweeps_root"]),
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
        product_name=account.get("product", "Apex Legacy 25K PA"),
        starting_balance_usd=float(account["starting_balance_usd"]),
        trailing_drawdown_usd=float(account["trailing_drawdown_usd"]),
        frozen_floor_profit_usd=float(account["frozen_floor_profit_usd"]),
        threshold_touch_fails=bool(account["threshold_touch_fails"]),
        purchase_fee_usd=float(account["purchase_fee_usd"]),
        replace_on_death=bool(book["replace_on_death"]),
        max_accounts=book["max_accounts"],
        rulebook=_legacy_rulebook(withdrawals),
        policy=policy,
    )


def config_from_payload(payload: dict) -> RunConfig:
    schema = payload.get("schema_version")
    if schema == SCENARIO_SCHEMA:
        return _from_scenario(payload)
    if schema == LEGACY_SCHEMA:
        return _from_legacy(payload)
    raise ValueError(f"Unsupported config schema: {schema!r}")


def to_payload(config: RunConfig) -> dict:
    """The fully resolved scenario, with every layer inlined."""

    try:
        sweeps_root = config.sweeps_root.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        sweeps_root = config.sweeps_root.as_posix()

    return {
        "schema_version": SCENARIO_SCHEMA,
        "scenario": config.scenario,
        "brick": config.brick,
        "brick_name": config.brick_name,
        "description": config.description,
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
        "product": {
            "product": config.product_name,
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
        "firm_rules": config.rulebook.to_payload(),
        "policy": config.policy.to_payload(),
    }


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> RunConfig:
    return config_from_payload(json.loads(Path(path).read_text(encoding="utf-8")))
