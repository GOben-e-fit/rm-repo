#!/usr/bin/env python3
"""Validate every metric contract YAML against schema.json.

Usage:
    python validate.py                              # validate everything under contracts/metric-contracts/
    python validate.py path/to/contract.yaml ...    # validate specific files

Exit code 0 = all valid, 1 = at least one invalid (CI release-blocker).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "schema.json").read_text(encoding="utf-8"))


def discover() -> list[Path]:
    """All .yaml under contracts/metric-contracts/ except this script's own files."""
    return [
        p
        for p in ROOT.rglob("*.yaml")
        if "schema" not in p.name.lower()
    ]


def validate_one(path: Path) -> list[str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return ["root must be a mapping"]
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(SCHEMA)
    for err in validator.iter_errors(data):
        loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    # extra rule: external_llm_allowed only with non-pii classifications
    if data.get("external_llm_allowed") and data.get("data_classification") in {"confidential", "pii"}:
        errors.append(
            "external_llm_allowed=true requires data_classification ∈ {public, internal}"
        )
    return errors


def main(argv: list[str]) -> int:
    paths = [Path(p) for p in argv[1:]] or discover()
    failed = 0
    for p in sorted(paths):
        errs = validate_one(p)
        if errs:
            failed += 1
            print(f"FAIL  {p.relative_to(ROOT.parent.parent) if ROOT.parent.parent in p.parents else p}")
            for e in errs:
                print(f"      - {e}")
        else:
            rel = p.relative_to(ROOT) if ROOT in p.parents else p
            print(f"OK    {rel}")
    print(f"\n{len(paths) - failed}/{len(paths)} contracts valid")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
