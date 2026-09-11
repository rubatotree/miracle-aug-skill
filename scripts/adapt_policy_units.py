"""Copy a LeRobot MEAN_STD checkpoint into explicit positive-affine hardware units.

Requires torch and safetensors. Does not connect hardware, train, upload, or establish
mechanical calibration. Mapping vectors have shape (D,); runtime tensors end in D.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

import torch
from safetensors import safe_open
from safetensors.torch import load_file, save_file

FEATURE_TYPES = {"observation.state": "STATE", "action": "ACTION"}
LOCATION_STATS = {"mean", "min", "max", "q01", "q10", "q50", "q90", "q99"}


def validate_mapping(mapping: dict[str, Any]) -> dict[str, tuple[torch.Tensor, torch.Tensor]]:
    """Resolve per-feature affine vectors (D_state,) and (D_action,), independently."""
    if not isinstance(mapping.get("evidence"), str) or not mapping["evidence"].strip():
        raise ValueError("Supply mapping evidence; do not guess a hardware calibration")
    if mapping.get("alignment_kind") not in {"measured", "official", "nominal", "synthetic_test"}:
        raise ValueError("Declare measured, official, nominal or synthetic_test alignment_kind")
    features = mapping.get("features", {})
    if set(features) != set(FEATURE_TYPES):
        raise ValueError("Explicit independent observation.state and action maps are required")
    result: dict[str, tuple[torch.Tensor, torch.Tensor]] = {}
    for feature, record in features.items():
        names = record.get("names", [])
        if not names or any(not isinstance(name, str) or not name.strip() for name in names) or len(set(names)) != len(names):
            raise ValueError(f"{feature} needs unique ordered coordinate names")
        for key in ("source_units", "target_units"):
            units = record.get(key, [])
            if len(units) != len(names) or any(not isinstance(unit, str) or not unit.strip() for unit in units):
                raise ValueError(f"{feature} needs one {key} entry per coordinate")
        scale = torch.as_tensor(record["scale"], dtype=torch.float64)
        offset = torch.as_tensor(record["offset"], dtype=torch.float64)
        if scale.shape != (len(names),) or offset.shape != scale.shape:
            raise ValueError(f"{feature} mapping shape must match its ordered names")
        if not torch.isfinite(scale).all() or not torch.isfinite(offset).all() or not (scale > 0).all():
            raise ValueError("Only finite positive scales and finite offsets are supported")
        result[feature] = scale, offset
    return result


def transform_statistics(values: dict[str, torch.Tensor],
                         mappings: dict[str, tuple[torch.Tensor, torch.Tensor]]) -> dict[str, torch.Tensor]:
    """Transform (D,) moments; preserve unrelated tensors, including images and counts.

    Broadcasting these moments preserves runtime state (B,D) and action (B,H,D) shapes.
    Normalizer epsilon and model rounding require a separate actual-runtime check.
    """
    result = {name: value.clone() for name, value in values.items()}
    for feature, (scale, offset) in mappings.items():
        matching = {name: value for name, value in values.items() if name.startswith(feature + ".")}
        if not matching:
            continue
        if any(f"{feature}.{stat}" not in values for stat in ("mean", "std")):
            raise ValueError(f"Missing {feature} mean/std")
        for name, tensor in matching.items():
            stat = name[len(feature) + 1:]
            if stat == "count":
                continue
            if stat not in LOCATION_STATS | {"std"}:
                raise ValueError(f"Unsupported coordinate statistic: {name}")
            if tensor.shape != scale.shape or not tensor.is_floating_point() or not torch.isfinite(tensor).all():
                raise ValueError(f"Invalid finite floating statistic shape: {name}")
            if stat == "std" and not (tensor > 0).all():
                raise ValueError(f"Nonpositive std requires explicit epsilon-aware handling: {name}")
            converted = tensor * scale.to(tensor)
            if stat != "std":
                converted = converted + offset.to(tensor)
            if not torch.isfinite(converted).all() or (stat == "std" and not (converted > 0).all()):
                raise ValueError(f"Mapping overflows or underflows storage precision: {name}")
            result[name] = converted
    return result


def local_file(root: Path, relative: str) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("Processor state files must be checkpoint-relative")
    if not path.is_file():
        raise ValueError(f"Missing checkpoint file: {relative}")
    return path


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def adapt_checkpoint(source: Path, output: Path, mapping: dict[str, Any]) -> dict[str, Any]:
    mappings = validate_mapping(mapping)
    source, output = source.resolve(), output.resolve()
    if not source.is_dir() or output.exists() or output.is_relative_to(source):
        raise ValueError("Use an existing source and a new separate output directory")
    if (source / "deployment_units.json").exists():
        raise ValueError("Source already has deployment units; refuse double adaptation")
    weights = sorted(set(source.glob("model*.safetensors")) | set(source.glob("pytorch_model*.bin")))
    if not weights:
        raise ValueError("No supported model weights found")
    weight_hashes = {path.name: checksum(path) for path in weights}
    replacements: dict[str, tuple[dict[str, torch.Tensor], dict[str, str] | None]] = {}
    endpoints: set[tuple[str, str]] = set()
    for pipeline_name, registry in (("policy_preprocessor", "normalizer_processor"),
                                    ("policy_postprocessor", "unnormalizer_processor")):
        pipeline = json.loads(local_file(source, pipeline_name + ".json").read_text())
        for step in pipeline["steps"]:
            if step.get("registry_name") != registry:
                continue
            config = step["config"]
            filename = step["state_file"]
            path = local_file(source, filename)
            values = load_file(str(path), device="cpu")
            active: dict[str, tuple[torch.Tensor, torch.Tensor]] = {}
            for feature, vectors in mappings.items():
                if not any(name.startswith(feature + ".") for name in values):
                    continue
                declaration = config.get("features", {}).get(feature)
                # The SDK can save all dataset statistics in an action-only pipeline.
                # Convert matching stored moments, but count only declared runtime endpoints.
                if declaration is not None:
                    if declaration.get("type") != FEATURE_TYPES[feature] or declaration.get("shape") != list(vectors[0].shape):
                        raise ValueError(f"Processor feature declaration disagrees with mapping: {feature}")
                    if config.get("norm_map", {}).get(FEATURE_TYPES[feature]) != "MEAN_STD":
                        raise ValueError("This helper supports MEAN_STD normalization only")
                    endpoint = pipeline_name, feature
                    if endpoint in endpoints:
                        raise ValueError(f"Repeated normalization of {feature} requires a custom adapter")
                    endpoints.add(endpoint)
                active[feature] = vectors
            if active:
                transformed = transform_statistics(values, active)
                with safe_open(str(path), framework="pt", device="cpu") as handle:
                    metadata = handle.metadata()
                if filename in replacements:
                    previous = replacements[filename][0]
                    if previous.keys() != transformed.keys() or any(not torch.equal(previous[k], transformed[k]) for k in previous):
                        raise ValueError("Shared processor state file has conflicting transformations")
                replacements[filename] = transformed, metadata
    required = {("policy_preprocessor", "observation.state"), ("policy_postprocessor", "action")}
    if not required.issubset(endpoints):
        raise ValueError("Both state preprocessing and action postprocessing must be adapted")
    # Construct in a temporary sibling; an interrupted conversion is not a final package.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".unit-adapter-", dir=output.parent) as temporary:
        staged = Path(temporary) / "policy"
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns(".cache", "__pycache__", "*.pyc"))
        for filename, (values, metadata) in replacements.items():
            save_file(values, str(staged / filename), metadata=metadata)
        if {name: checksum(staged / name) for name in weight_hashes} != weight_hashes:
            raise ValueError("Policy weights changed during adaptation")
        report = {
            "schema": "miracleaug_affine_deployment_v1", "mapping": deepcopy(mapping),
            "equation": "hardware = scale * training_coordinate + offset",
            "model_weights_unchanged": True, "weight_sha256": weight_hashes,
            "changed_stat_files": sorted(replacements),
            "processor_endpoints": [list(endpoint) for endpoint in sorted(endpoints)],
            "actual_runtime_verified": False, "physical_calibration_verified": False,
            "real_task_success_verified": False,
            "limitations": ["Names/units are supplied, not inferred from physical hardware.",
                            "Verify normalization epsilon and network rounding with the actual runtime.",
                            "Load both processors; do not apply the mapping again outside them."],
        }
        (staged / "deployment_units.json").write_text(json.dumps(report, indent=2) + "\n")
        previous_card = (staged / "README.md").read_text() if (staged / "README.md").exists() else ""
        (staged / "README.md").write_text(
            "# Deployment coordinate adaptation\n\n"
            "Load both saved processors. Their units are declared in deployment_units.json; "
            "model weights are unchanged. Original metrics below remain in training units. "
            "Actual runtime, physical calibration and task success are not verified by this helper.\n\n"
            + previous_card)
        if output.exists():
            raise ValueError("Output appeared during conversion; refusing overwrite")
        staged.rename(output)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = adapt_checkpoint(args.checkpoint, args.output, json.loads(args.mapping.read_text()))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
