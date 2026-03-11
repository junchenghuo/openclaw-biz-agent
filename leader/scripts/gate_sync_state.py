#!/usr/bin/env python3
"""Sync gate progress into plan/STATE.json from plan/TASKS.json.

Example:
  python3 leader/scripts/gate_sync_state.py --project projects/login-page-delivery
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


WORKSPACE_ROOT = Path("/Users/imac/midCreate/openclaw-workspaces/ai-team")
GATE_ORDER = [
    "gate0_requirements",
    "gate1_product_review",
    "gate2_arch_design_review",
    "gate3_dev",
    "gate4_test",
    "gate5_deploy",
]


def now_local_iso() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).replace(microsecond=0).isoformat()


def resolve_project_root(project_value: str) -> Path:
    value = project_value.strip()
    if not value:
        raise ValueError("--project is required")
    if value.startswith("/"):
        return Path(value)
    return (WORKSPACE_ROOT / value).resolve()


def load_tasks(tasks_file: Path) -> list[dict]:
    if not tasks_file.exists():
        raise ValueError(f"TASKS file not found: {tasks_file}")
    raw = json.loads(tasks_file.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict) and isinstance(raw.get("tasks"), list):
        return [item for item in raw["tasks"] if isinstance(item, dict)]
    raise ValueError(f"Unsupported TASKS format: {tasks_file}")


def load_state(state_file: Path) -> dict:
    if not state_file.exists():
        return {}
    raw = json.loads(state_file.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw
    raise ValueError(f"Unsupported STATE format: {state_file}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync gate progress to STATE.json")
    parser.add_argument(
        "--project", required=True, help="project path (e.g. projects/foo)"
    )
    args = parser.parse_args()

    project_root = resolve_project_root(args.project)
    tasks_file = project_root / "plan" / "TASKS.json"
    state_file = project_root / "plan" / "STATE.json"

    tasks = load_tasks(tasks_file)
    state = load_state(state_file)

    gates: dict = {}
    passed_until = True
    next_dispatch_gate: Optional[str] = None
    blocked_by: list[str] = []

    for gate in GATE_ORDER:
        gate_tasks = [
            task for task in tasks if str(task.get("gate", "")).strip() == gate
        ]
        total = len(gate_tasks)
        done = sum(
            1 for task in gate_tasks if str(task.get("status", "")).strip() == "done"
        )
        passed = total == 0 or done == total
        waiting = total > 0 and done < total

        gates[gate] = {
            "total": total,
            "done": done,
            "passed": passed,
            "waiting": waiting,
        }

        if passed_until and waiting and next_dispatch_gate is None:
            next_dispatch_gate = gate
        if passed_until and total > 0 and not passed:
            passed_until = False
            blocked_by.append(gate)

    if next_dispatch_gate is None:
        # If all defined gates passed, no next gate is pending.
        next_dispatch_gate = "completed"

    state["stageControl"] = {
        "updatedAt": now_local_iso(),
        "gateOrder": GATE_ORDER,
        "gates": gates,
        "nextDispatchGate": next_dispatch_gate,
        "blockedBy": blocked_by,
    }

    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"PROJECT={project_root}")
    print(f"STATE_FILE={state_file}")
    print(f"NEXT_DISPATCH_GATE={next_dispatch_gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
