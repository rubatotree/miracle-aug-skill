"""Finite augmentation ledger. Domain checks are supplied by the project adapter."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import os
from typing import Any, Iterator
import uuid

FAMILIES = ("camera_static", "camera_dynamic", "lighting_static", "lighting_dynamic",
            "material", "environment", "object_pose", "object_style", "trajectory", "mixed")
CHECKS = {"scene": ("source_match", "editable_geometry", "motion", "view_coverage"),
          "dataset": ("native_reader", "video_alignment", "trajectory_contract", "quota_counts")}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{uuid.uuid4().hex}.partial")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def checksum(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError(f"Artifact must stay inside the project: {relative}")
    return path


def artifact_hashes(root: Path, paths: list[str]) -> dict[str, str]:
    if not paths or len(set(paths)) != len(paths):
        raise ValueError("Evidence requires nonempty, unique artifact paths")
    return {name: checksum(inside(root, name)) for name in paths}


@contextmanager
def ledger_lock(root: Path) -> Iterator[None]:
    """One coordinator mutates the ledger; workers only produce independent receipts."""
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".ledger.lock").open("a+b") as handle:
        if os.name == "nt":
            import msvcrt
            handle.seek(0)
            if not handle.read(1):
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def allocate(total: int, weights: dict[str, int]) -> dict[str, int]:
    if type(total) is not int or total < 0 or any(type(w) is not int or w < 0 for w in weights.values()):
        raise ValueError("Counts and weights must be nonnegative integers")
    denominator = sum(weights.values())
    if denominator == 0:
        if total:
            raise ValueError("Cannot allocate a positive total to zero weights")
        return {name: 0 for name in weights}
    counts = {name: total * weight // denominator for name, weight in weights.items()}
    order = sorted(weights, key=lambda name: (-(total * weights[name] % denominator), name))
    for name in order[:total - sum(counts.values())]:
        counts[name] += 1
    return counts


def validate_request(request: dict[str, Any]) -> None:
    total = request["accepted_count"]
    if type(total) is not int or total <= 0 or total > request["authorized_limit"]:
        raise ValueError("A positive count within the authorized limit is required for generation")
    quotas = request["quotas"]
    for quota in quotas.values():
        if any(type(quota[k]) is not int for k in ("count", "weak")) or not 0 <= quota["weak"] <= quota["count"]:
            raise ValueError("Invalid weak/family count")
    if sum(q["count"] for q in quotas.values()) != total:
        raise ValueError("Family counts must sum to the accepted count")
    if set(request["engines"]) != {"CYCLES", "BLENDER_EEVEE"}:
        raise ValueError("Specify both engine counts, including zero when unused")
    for profile in request["engines"].values():
        if type(profile["count"]) is not int or profile["count"] < 0 or type(profile["samples"]) is not int or profile["samples"] <= 0:
            raise ValueError("Invalid render profile")
        if not math.isfinite(profile["weight"]) or profile["weight"] < 0:
            raise ValueError("Invalid training weight")
    if sum(p["count"] for p in request["engines"].values()) != total:
        raise ValueError("Engine counts must sum to the accepted count")
    if type(request["attempts_per_episode"]) is not int or request["attempts_per_episode"] < 1:
        raise ValueError("Invalid finite candidate budget")


def verify_evidence(root: Path, record: dict[str, Any]) -> dict[str, Any]:
    if checksum(inside(root, record["report"])) != record["report_sha256"]:
        raise ValueError("Evidence report changed")
    if artifact_hashes(root, list(record["artifacts"])) != record["artifacts"]:
        raise ValueError("Evidence artifact changed")
    return read_json(inside(root, record["report"]))


def checkpoint(root: Path, name: str, report_path: str) -> None:
    report = read_json(inside(root, report_path))
    if report.get("passed") is not True or not all(report.get("checks", {}).get(k) is True for k in CHECKS[name]):
        raise ValueError(f"Passing {name} checks are required")
    record = {"report": report_path, "report_sha256": checksum(inside(root, report_path)),
              "artifacts": artifact_hashes(root, report["artifacts"]),
              "request_sha256": checksum(root / "request.json")}
    path = root / "checkpoints" / (name + ".json")
    if path.exists() and read_json(path) != record and (root / "plan.json").exists():
        raise ValueError("Frozen checkpoint changed; create a new session")
    write_json(path, record)


def verify_checkpoint(root: Path, name: str) -> dict[str, Any]:
    record = read_json(root / "checkpoints" / (name + ".json"))
    if record["request_sha256"] != checksum(root / "request.json"):
        raise ValueError("Request changed after checkpoint")
    return verify_evidence(root, record)


def create_plan(root: Path) -> dict[str, Any]:
    request = read_json(root / "request.json")
    validate_request(request)
    verify_checkpoint(root, "scene")
    if (root / "plan.json").exists():
        return load_plan(root)
    strata_weights = {f"{family}/{strength}": number for family, quota in request["quotas"].items()
                      for strength, number in (("weak", quota["weak"]), ("strong", quota["count"] - quota["weak"])) if number}
    cycles = allocate(request["engines"]["CYCLES"]["count"], strata_weights)
    strata: dict[str, Any] = {}
    candidates: list[dict[str, Any]] = []
    for base, count in strata_weights.items():
        for engine, required in (("CYCLES", cycles[base]), ("BLENDER_EEVEE", count - cycles[base])):
            if not required:
                continue
            key = f"{base}/{engine}"
            identifiers = []
            for _ in range(required * request["attempts_per_episode"]):
                identifier = f"candidate_{len(candidates):07d}"
                seed = int.from_bytes(hashlib.sha256(f"{request['seed']}:{identifier}".encode()).digest()[:8], "big")
                candidates.append({"id": identifier, "stratum": key, "seed": seed,
                                   "engine": engine, "profile": request["engines"][engine]})
                identifiers.append(identifier)
            strata[key] = {"required": required, "candidates": identifiers}
    plan = {"request_sha256": checksum(root / "request.json"), "scene_checkpoint_sha256": checksum(root / "checkpoints/scene.json"),
            "strata": strata, "candidates": candidates}
    write_json(root / "plan.json", plan)
    write_json(root / "state.json", {"plan_sha256": checksum(root / "plan.json"), "phase": "planned", "receipts": {}})
    return plan


def load_plan(root: Path) -> dict[str, Any]:
    plan = read_json(root / "plan.json")
    state = read_json(root / "state.json")
    if state["plan_sha256"] != checksum(root / "plan.json") or plan["request_sha256"] != checksum(root / "request.json"):
        raise ValueError("Frozen plan/request changed")
    if plan["scene_checkpoint_sha256"] != checksum(root / "checkpoints/scene.json"):
        raise ValueError("Frozen scene checkpoint changed")
    verify_checkpoint(root, "scene")
    return plan


def pending(root: Path) -> list[dict[str, Any]]:
    plan = load_plan(root)
    state = read_json(root / "state.json")
    lookup = {c["id"]: c for c in plan["candidates"]}
    result = []
    for stratum in plan["strata"].values():
        accepted = sum(state["receipts"].get(i, {}).get("outcome") == "accepted" for i in stratum["candidates"])
        if accepted >= stratum["required"]:
            continue
        unresolved = [i for i in stratum["candidates"] if i not in state["receipts"]]
        if not unresolved:
            raise ValueError("Candidate pool exhausted; no identity substitution or automatic expansion")
        result.append(lookup[unresolved[0]])
    return result


def record_receipt(root: Path, receipt_path: str) -> None:
    plan = load_plan(root)
    state = read_json(root / "state.json")
    receipt = read_json(inside(root, receipt_path))
    identifier = receipt["candidate_id"]
    if receipt["plan_sha256"] != state["plan_sha256"]:
        raise ValueError("Receipt belongs to a different plan")
    record = {"report": receipt_path, "report_sha256": checksum(inside(root, receipt_path)),
              "artifacts": artifact_hashes(root, receipt["artifacts"]), "outcome": receipt["outcome"]}
    if identifier in state["receipts"]:
        if state["receipts"][identifier] != record:
            raise ValueError("Conflicting receipt for completed candidate")
        return
    if identifier not in {c["id"] for c in pending(root)}:
        raise ValueError("Candidate is not the next authorized candidate in its stratum")
    if receipt["outcome"] == "accepted":
        required = ["geometry", "task_success", "visibility", "render_complete", "labels"]
        if read_json(root / "request.json")["privacy"]["redact_exterior"]:
            required.append("privacy")
        if not all(receipt.get("checks", {}).get(k) is True for k in required):
            raise ValueError("Acceptance requires all real task/render/label checks")
    elif receipt["outcome"] != "rejected" or not receipt.get("reason"):
        raise ValueError("Only checked acceptance or reasoned semantic rejection consumes a candidate")
    state["receipts"][identifier] = record
    state["phase"] = "generating"
    write_json(root / "state.json", state)


def seal(root: Path) -> dict[str, Any]:
    plan = load_plan(root)
    if pending(root):
        raise ValueError("Accepted quotas remain incomplete")
    state = read_json(root / "state.json")
    for record in state["receipts"].values():
        verify_evidence(root, record)
    report = verify_checkpoint(root, "dataset")
    accepted = sorted(i for i, r in state["receipts"].items() if r["outcome"] == "accepted")
    if sorted(report.get("accepted_candidate_ids", [])) != accepted:
        raise ValueError("Native dataset report must bind exactly the accepted candidates")
    if len(accepted) != sum(s["required"] for s in plan["strata"].values()):
        raise ValueError("Internal exact-count invariant failed")
    state.update(phase="complete", accepted_candidates=accepted)
    write_json(root / "state.json", state)
    return {"complete": True, "accepted": len(accepted), "upload_verified": False}


def initialize(args: argparse.Namespace) -> None:
    root = args.root
    if (root / "request.json").exists():
        raise ValueError("Project request exists; inspect it instead of overwriting")
    if args.count < 0 or not 0 <= (args.cycles or 0) <= args.count:
        raise ValueError("Invalid accepted/engine counts")
    count = args.count
    cycles = args.cycles if args.cycles is not None else (count + 2) // 5
    counts = allocate(count, dict.fromkeys(FAMILIES, 1))
    weak = allocate((count + 2) // 5, counts)
    kind, source = next((kind, value) for kind, value in (("hf", args.hf_dataset), ("dataset", args.dataset), ("video", args.video)) if value)
    request = {"schema": "miracleaug_request_v1", "source": {"kind": kind, "location": source, "episode": args.episode},
               "task": args.task, "references": args.reference, "accepted_count": count, "authorized_limit": count,
               "seed": args.seed, "attempts_per_episode": 12,
               "quotas": {f: {"count": counts[f], "weak": weak[f]} for f in FAMILIES},
               "engines": {"CYCLES": {"count": cycles, "samples": 128, "weight": 1.0},
                           "BLENDER_EEVEE": {"count": count - cycles, "samples": 64, "weight": 1.0}},
               "privacy": {"redact_exterior": args.redact_exterior},
               "preview": {"formats": ["png", "mp4"], "grid": [6, 6], "scales": [1, 2, 4]},
               "upload": {"enabled": False, "repo_id": None, "private": True}}
    if count:
        validate_request(request)
    write_json(root / "request.json", request)
    (root / "docs").mkdir(exist_ok=True)
    if not (root / "ROADMAP.md").exists():
        (root / "ROADMAP.md").write_text("# MiracleAug project\n\nArchitecture: source contract → metric scene/task adapter → finite generation → native export/validation.\n\nMilestones: source inspection; calibrated editable scene checkpoint; task-aware augmentation; render smoke; exact accepted dataset; authorized upload/evaluation.\n\nRisks: partial observability, control semantics, contact feasibility, renderer differences, privacy, compute/storage.\n", encoding="utf-8")
    if not (root / "docs/dev_log.md").exists():
        (root / "docs/dev_log.md").write_text("# Execution evidence\n\nRequest initialized; reconstruction and generation have not yet been validated.\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "checkpoint", "plan", "next", "record", "seal", "status"))
    parser.add_argument("--root", type=Path, required=True)
    sources = parser.add_mutually_exclusive_group()
    sources.add_argument("--hf-dataset")
    sources.add_argument("--dataset")
    sources.add_argument("--video")
    parser.add_argument("--episode", type=int, default=0)
    parser.add_argument("--task", default="Inspect source task")
    parser.add_argument("--count", type=int, default=0)
    parser.add_argument("--cycles", type=int)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--redact-exterior", action="store_true")
    parser.add_argument("--name", choices=tuple(CHECKS))
    parser.add_argument("--report")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    args.root = args.root.resolve()
    if args.episode < 0:
        parser.error("Episode must be nonnegative")
    if args.command == "init" and not any((args.hf_dataset, args.dataset, args.video)):
        parser.error("init requires a source")
    with ledger_lock(args.root):
        if args.command == "init":
            initialize(args)
            result: Any = {"request": str(args.root / "request.json")}
        elif args.command == "checkpoint":
            if not args.name or not args.report:
                parser.error("checkpoint requires --name and --report")
            checkpoint(args.root, args.name, args.report)
            result = {"checkpoint": args.name}
        elif args.command == "plan":
            plan = create_plan(args.root)
            result = {"candidates": len(plan["candidates"]), "strata": {k: v["required"] for k, v in plan["strata"].items()}}
        elif args.command == "next":
            result = pending(args.root)
        elif args.command == "record":
            if not args.receipt:
                parser.error("record requires --receipt")
            record_receipt(args.root, args.receipt)
            result = {"recorded": args.receipt}
        elif args.command == "seal":
            result = seal(args.root)
        else:
            load_plan(args.root)
            state = read_json(args.root / "state.json")
            result = {"phase": state["phase"], "accepted": sum(r["outcome"] == "accepted" for r in state["receipts"].values()),
                      "rejected": sum(r["outcome"] == "rejected" for r in state["receipts"].values())}
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
