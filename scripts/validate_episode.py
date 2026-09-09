"""Validate canonical frame shapes and timing; no claim of geometric task success."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from project import checksum, write_json


def vector(value: Any, size: int, name: str) -> list[float]:
    if not isinstance(value, list) or len(value) != size or any(type(v) not in (int, float) or not math.isfinite(v) for v in value):
        raise ValueError(f"Invalid finite vector {name}, expected shape ({size},)")
    return value


def matrix(value: Any, size: int, name: str, rigid: bool = False) -> None:
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"Invalid matrix {name}")
    for row in value:
        vector(row, size, name)
    if rigid:
        if any(abs(a - b) > 1e-5 for a, b in zip(value[-1], [0, 0, 0, 1])):
            raise ValueError("Invalid homogeneous transform row")
        for i in range(3):
            for j in range(3):
                dot = sum(value[k][i] * value[k][j] for k in range(3))
                if abs(dot - (1 if i == j else 0)) > 1e-4:
                    raise ValueError("Transform rotation is not orthonormal")
        determinant = sum(value[0][i] * (value[1][(i+1)%3] * value[2][(i+2)%3] - value[1][(i+2)%3] * value[2][(i+1)%3]) for i in range(3))
        if determinant < 0.999:
            raise ValueError("Transform contains a reflection")


def validate(schema: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Rows have states (T,D_state), actions (T,D_action), K (T,C,3,3), poses (T,C,4,4)."""
    if not rows:
        raise ValueError("Empty episode")
    state_size, action_size = len(schema["state_names"]), len(schema["action_names"])
    if not state_size or not action_size or len(set(schema["state_names"])) != state_size or len(set(schema["action_names"])) != action_size:
        raise ValueError("Empty or duplicate state/action names")
    if len(schema["state_units"]) != state_size or len(schema["action_units"]) != action_size:
        raise ValueError("Unit dimensions differ from features")
    semantics = schema["action_semantics"]
    if semantics not in ("next_position_target", "recorded_command", "synthesized_command"):
        raise ValueError("Explicit action semantics required")
    if semantics == "next_position_target" and (schema["state_names"] != schema["action_names"] or schema["state_units"] != schema["action_units"]):
        raise ValueError("Next-position targets require matching state/action coordinates and units")
    fps = schema.get("fps")
    if fps is not None and (not math.isfinite(fps) or fps <= 0):
        raise ValueError("FPS must be positive or null for irregular timestamps")
    cameras = schema["cameras"]
    if not cameras:
        raise ValueError("At least one reconstructed camera is required")
    previous_time = -math.inf
    for index, row in enumerate(rows):
        if row["frame_index"] != index:
            raise ValueError("Noncontiguous frame indices")
        timestamp = row["timestamp"]
        if not math.isfinite(timestamp) or timestamp < 0 or timestamp <= previous_time:
            raise ValueError("Nonmonotonic/nonfinite timestamps")
        if fps and abs(timestamp - rows[0]["timestamp"] - index / fps) > 1e-4:
            raise ValueError("Frames do not match the declared CFR timeline")
        previous_time = timestamp
        state = vector(row["observation.state"], state_size, "state")
        action = vector(row["action"], action_size, "action")
        if type(row["action_valid"]) is not bool:
            raise ValueError("Action validity must be Boolean")
        if semantics == "next_position_target":
            target = rows[index + 1]["observation.state"] if index + 1 < len(rows) else state
            vector(target, state_size, "next state")
            if any(abs(a - b) > 1e-5 for a, b in zip(action, target)) or row["action_valid"] != (index + 1 < len(rows)):
                raise ValueError("Next-position alignment or terminal validity failed")
        if set(row["cameras"]) != set(cameras):
            raise ValueError("Camera channels differ from schema")
        for name in cameras:
            camera = row["cameras"][name]
            matrix(camera["intrinsics"], 3, name + " K")
            matrix(camera["world_from_camera"], 4, name + " pose", rigid=True)
            if camera["intrinsics"][0][0] <= 0 or camera["intrinsics"][1][1] <= 0:
                raise ValueError("Nonpositive focal length")
            if not math.isfinite(camera["timestamp"]) or abs(camera["timestamp"] - timestamp) > schema.get("camera_tolerance_s", 1e-4):
                raise ValueError("Camera/state timestamp mismatch")
        if row["render.engine"] not in ("CYCLES", "BLENDER_EEVEE"):
            raise ValueError("Unknown renderer")
        weight = row["training.sample_weight"]
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Invalid training weight")
        if schema.get("privacy_required") and row.get("privacy.redacted") is not True:
            raise ValueError("Missing per-frame privacy release")
    return {"passed": True, "frames": len(rows), "state_dimension": state_size, "action_dimension": action_size,
            "cameras": cameras, "action_semantics": semantics, "geometry_checked": False, "native_sdk_checked": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in args.frames.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = validate(schema, rows)
    report.update(schema_sha256=checksum(args.schema), frames_sha256=checksum(args.frames))
    write_json(args.report, report)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
