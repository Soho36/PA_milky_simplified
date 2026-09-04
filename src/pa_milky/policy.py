"""Our own withdrawal behaviour, kept strictly apart from the firm's rules.

The firm decides what is *allowed*. This decides what we *ask for*, and how
often. Nothing here is a rule we have to obey; every field is a lever we chose.
"""

from __future__ import annotations

from dataclasses import dataclass

CADENCES = ("never", "calendar_month")
AMOUNT_RULES = ("fixed", "maximum", "minimum")
SHORTFALL_RULES = ("skip", "accrue_backlog", "partial")

# Stands in for "ask for everything the rules permit". Larger than any balance
# this study can reach, so the firm's caps are always what bind.
UNBOUNDED_REQUEST_USD = 1_000_000_000.0


@dataclass(frozen=True, slots=True)
class WithdrawalPolicy:
    name: str = "hold"
    cadence: str = "never"
    amount_usd: float = 0.0
    amount_rule: str = "fixed"
    shortfall: str = "skip"
    quantize_to_amount: bool = True

    def __post_init__(self) -> None:
        if self.cadence not in CADENCES:
            raise ValueError(f"Unknown cadence: {self.cadence!r}")
        if self.amount_rule not in AMOUNT_RULES:
            raise ValueError(f"Unknown amount rule: {self.amount_rule!r}")
        if self.shortfall not in SHORTFALL_RULES:
            raise ValueError(f"Unknown shortfall rule: {self.shortfall!r}")
        if self.enabled and self.amount_rule == "fixed" and self.amount_usd <= 0:
            raise ValueError("A fixed-amount policy needs a positive amount")

    @property
    def enabled(self) -> bool:
        return self.cadence != "never"

    @property
    def keeps_backlog(self) -> bool:
        return self.shortfall != "skip"

    def requested_usd(self, account, *, firm_minimum_usd: float) -> float:
        """What we ask the firm for at this decision."""

        if self.amount_rule == "maximum":
            return UNBOUNDED_REQUEST_USD
        if self.amount_rule == "minimum":
            return firm_minimum_usd
        return account.entitlement_outstanding_usd

    def quantizer(self):
        """Round an allowed amount down to whole units of our monthly ask.

        Only meaningful for a fixed ask: it keeps the pocket a clean multiple of
        the target and stops a backlog being paid in odd fragments.
        """

        if not (self.quantize_to_amount and self.amount_rule == "fixed"):
            return None
        step = self.amount_usd

        def quantize(allowed: float) -> float:
            if allowed < step:
                return 0.0
            return round(int(allowed // step) * step, 2)

        return quantize

    def to_payload(self) -> dict:
        return {
            "name": self.name,
            "cadence": self.cadence,
            "amount_usd": self.amount_usd,
            "amount_rule": self.amount_rule,
            "shortfall": self.shortfall,
            "quantize_to_amount": self.quantize_to_amount,
        }

    @classmethod
    def from_payload(cls, payload: dict) -> "WithdrawalPolicy":
        return cls(
            name=payload.get("name", "unnamed"),
            cadence=payload.get("cadence", "never"),
            amount_usd=float(payload.get("amount_usd", 0.0)),
            amount_rule=payload.get("amount_rule", "fixed"),
            shortfall=payload.get("shortfall", "skip"),
            quantize_to_amount=bool(payload.get("quantize_to_amount", True)),
        )
