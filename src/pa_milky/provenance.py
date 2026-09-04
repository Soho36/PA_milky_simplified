"""Sealing a brick's result so later bricks are measured, not just compared.

A sealed baseline is three things at once:

1. the exact config that produced it, embedded rather than referenced, so a
   later edit to ``config/runtime.json`` cannot retroactively rewrite history;
2. digests of every input file, every engine module, and every output file;
3. the headline numbers, written out in full.

Verification re-runs the sealed config against *today's* engine and compares
the numbers. Engine drift is expected as later bricks land and is reported, not
failed, and so is presentation drift in report.txt. What must not move is the
measurement: every headline value and every field a sealed summary recorded.
Later bricks may *add* fields; they may not change a pinned one.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from .config import PROJECT_ROOT, RunConfig, config_from_payload, to_payload
from .loader import WINDOWS, load_trades

MANIFEST_SCHEMA = "pa_milky_simplified.baseline.v1"
BASELINE_ROOT = PROJECT_ROOT / "baselines"
ENGINE_DIR = Path(__file__).resolve().parent
OUTPUT_NAMES = ("summary.json", "accounts.csv", "report.txt")
# Written only by bricks that produce them; sealed when present.
OPTIONAL_OUTPUT_NAMES = ("withdrawals.csv", "denials.csv", "ablation.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _combined(entries: list[tuple[str, str, int]]) -> str:
    """Order-independent digest over (name, sha256, bytes) triples."""

    digest = hashlib.sha256()
    for name, file_hash, size in sorted(entries):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(file_hash))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _digest_tree(files: dict[str, Path]) -> dict:
    entries = [
        (name, sha256_file(path), path.stat().st_size) for name, path in sorted(files.items())
    ]
    return {
        "files": {name: {"sha256": h, "bytes": b} for name, h, b in entries},
        "combined_sha256": _combined(entries),
        "count": len(entries),
        "bytes": sum(b for _, _, b in entries),
    }


def input_digest(config: RunConfig) -> dict:
    """Hash the 23 trade exports and 23 stats files this run actually reads."""

    files: dict[str, Path] = {}
    for window in WINDOWS:
        trades = (
            config.sweeps_root / config.strategy / window
            / f"{window}_{config.risk_reward}.csv"
        )
        stats = (
            config.sweeps_root / f"{config.strategy}_stats" / window
            / f"{window}_{config.risk_reward}_stats.csv"
        )
        files[f"{config.strategy}/{window}"] = trades
        files[f"{config.strategy}_stats/{window}"] = stats
    return _digest_tree(files)


def engine_digest() -> dict:
    files = {path.name: path for path in sorted(ENGINE_DIR.glob("*.py"))}
    return _digest_tree(files)


def git_revision() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    revision = completed.stdout.strip()
    return revision if completed.returncode == 0 and revision else None


def headline(summary: dict) -> dict:
    """The numbers a later brick is allowed to move only on purpose."""

    pinned = {
        "trades_loaded": summary["tape"]["trades_loaded"],
        "copies_filled": summary["tape"]["copies_filled"],
        "accounts_opened": summary["book"]["accounts_opened"],
        "accounts_alive_at_end": summary["book"]["accounts_alive_at_end"],
        "accounts_dead": summary["book"]["accounts_dead"],
        "spent_on_accounts_usd": summary["cash"]["spent_on_accounts_usd"],
        "withdrawn_usd": summary["cash"]["withdrawn_usd"],
        "owner_cash_position_usd": summary["cash"]["owner_cash_position_usd"],
        "total_balance_usd": summary["alive_equity"]["total_balance_usd"],
        "total_paper_profit_usd": summary["alive_equity"]["total_paper_profit_usd"],
    }
    denials = summary.get("denials")
    if denials:
        pinned["requests_approved"] = denials["requests_approved"]
        pinned["requests_denied"] = denials["requests_denied"]
    withdrawals = summary.get("withdrawals")
    if withdrawals:
        pinned["withdrawal_events"] = withdrawals["events"]
        pinned["accounts_that_ever_paid"] = withdrawals["accounts_that_ever_paid"]
        pinned["entitlement_accrued_usd"] = withdrawals["entitlement_accrued_usd"]
        pinned["outstanding_lost_to_deaths_usd"] = withdrawals[
            "outstanding_lost_to_deaths_usd"
        ]
    return pinned


def seal(name: str, config: RunConfig, summary: dict, output_dir: Path) -> Path:
    """Write ``baselines/<name>/`` from an already-written output directory."""

    destination = BASELINE_ROOT / name
    destination.mkdir(parents=True, exist_ok=True)
    sealed_names = list(OUTPUT_NAMES)
    for filename in OPTIONAL_OUTPUT_NAMES:
        if (output_dir / filename).is_file():
            sealed_names.append(filename)
    for filename in sealed_names:
        (destination / filename).write_bytes((output_dir / filename).read_bytes())

    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "baseline": name,
        "brick": config.brick,
        "brick_name": config.brick_name,
        "sealed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_revision": git_revision(),
        "config": to_payload(config),
        "inputs": input_digest(config),
        "engine": engine_digest(),
        "outputs": _digest_tree({n: destination / n for n in sealed_names}),
        "headline": headline(summary),
    }
    manifest_path = destination / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def _pinned_differences(sealed, actual, *, path: str) -> list[str]:
    """Every value the seal recorded must still be there, unchanged."""

    if isinstance(sealed, dict):
        if not isinstance(actual, dict):
            return [f"{path}: was an object, now {type(actual).__name__}"]
        differences: list[str] = []
        for key, value in sealed.items():
            if key == "generated_utc":
                continue
            if key not in actual:
                differences.append(f"{path}.{key}: pinned value has disappeared")
                continue
            differences.extend(_pinned_differences(value, actual[key], path=f"{path}.{key}"))
        return differences
    if sealed != actual:
        return [f"{path}: sealed {sealed!r}, now {actual!r}"]
    return []


@dataclass(frozen=True, slots=True)
class VerificationResult:
    baseline: str
    ok: bool
    failures: list[str]
    notes: list[str]

    def render(self) -> str:
        lines = [f"baseline {self.baseline}: {'OK' if self.ok else 'FAILED'}"]
        lines += [f"  FAIL  {message}" for message in self.failures]
        lines += [f"  note  {message}" for message in self.notes]
        return "\n".join(lines)


def verify(name: str) -> VerificationResult:
    """Re-run a sealed config on today's engine and compare what came out."""

    # Imported here: report and simulator both import config, and provenance is
    # imported by the CLI before either of them is needed.
    from .report import summarize
    from .simulator import run_book

    destination = BASELINE_ROOT / name
    manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise ValueError(f"Unsupported baseline schema in {name}")

    failures: list[str] = []
    notes: list[str] = []
    config = config_from_payload(manifest["config"])

    current_inputs = input_digest(config)
    if current_inputs["combined_sha256"] != manifest["inputs"]["combined_sha256"]:
        failures.append(
            "the input tape has changed since the baseline was sealed "
            f"({manifest['inputs']['combined_sha256'][:12]} -> "
            f"{current_inputs['combined_sha256'][:12]})"
        )

    current_engine = engine_digest()
    if current_engine["combined_sha256"] != manifest["engine"]["combined_sha256"]:
        notes.append(
            "engine has changed since sealing, which is expected as later "
            "bricks land; the outputs below are what must still match"
        )

    summary = summarize(run_book(load_trades(
        config.sweeps_root, strategy=config.strategy, risk_reward=config.risk_reward
    ), config))
    sealed_headline = manifest["headline"]
    for key, expected in sealed_headline.items():
        actual = headline(summary).get(key)
        if actual != expected:
            failures.append(f"headline {key}: sealed {expected!r}, now {actual!r}")

    # summary.json carries a generation timestamp, so its content is compared
    # rather than its digest, and only what the seal actually recorded: a later
    # brick may add fields, but every pinned value must still come back.
    sealed_summary = json.loads((destination / "summary.json").read_text(encoding="utf-8"))
    failures.extend(_pinned_differences(sealed_summary, summary, path="summary"))

    return VerificationResult(
        baseline=name, ok=not failures, failures=failures, notes=notes
    )


def list_baselines() -> list[str]:
    if not BASELINE_ROOT.is_dir():
        return []
    return sorted(
        path.name for path in BASELINE_ROOT.iterdir() if (path / "manifest.json").is_file()
    )
