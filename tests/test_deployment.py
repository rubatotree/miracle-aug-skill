"""Synthetic deployment contracts; no real calibration, model download or hardware."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
HAS_DEPLOYMENT = bool(importlib.util.find_spec("torch") and importlib.util.find_spec("safetensors"))
if HAS_DEPLOYMENT:
    import torch
    from safetensors import safe_open
    from safetensors.torch import load_file, save_file
    from adapt_policy_units import adapt_checkpoint, transform_statistics, validate_mapping


def mapping_fixture() -> dict[str, object]:
    # Deliberately use unequal state/action dimensions, no SO101 naming or coefficients.
    return {"evidence": "Synthetic independent affine maps", "alignment_kind": "synthetic_test",
            "features": {"observation.state": {"names": ["a", "b", "c"],
                "source_units": ["rad"] * 3, "target_units": ["deg"] * 3,
                "scale": [2., 3., 4.], "offset": [1., -5., 9.]},
                "action": {"names": ["jaw", "rotation"], "source_units": ["rad"] * 2,
                "target_units": ["percent", "deg"], "scale": [5., 7.], "offset": [3., -2.]}}}


def checkpoint_fixture(root: Path) -> None:
    root.mkdir()
    save_file({"synthetic_weight": torch.ones(2)}, str(root / "model.safetensors"))
    for name, registry in (("policy_preprocessor", "normalizer_processor"),
                           ("policy_postprocessor", "unnormalizer_processor")):
        features = {"action": {"type": "ACTION", "shape": [2]}}
        if name == "policy_preprocessor":
            features["observation.state"] = {"type": "STATE", "shape": [3]}
        values = {f"{feature}.{stat}": torch.full(tuple(record["shape"]), value)
                  for feature, record in features.items() for stat, value in (("mean", .25), ("std", .5))}
        # Real SDK checkpoints may retain unused state moments in action-only postprocessing.
        values.setdefault("observation.state.mean", torch.full((3,), .25))
        values.setdefault("observation.state.std", torch.full((3,), .5))
        values["observation.images.camera.mean"] = torch.ones((3, 1, 1))
        save_file(values, str(root / (name + ".safetensors")), metadata={"fixture": "synthetic"})
        (root / (name + ".json")).write_text(json.dumps({"steps": [{"registry_name": registry,
            "config": {"features": features, "norm_map": {"STATE": "MEAN_STD", "ACTION": "MEAN_STD"}},
            "state_file": name + ".safetensors"}]}))


class IntakeTests(unittest.TestCase):
    def test_primary_input_and_photo_fallback_scope(self) -> None:
        for source in (["--hf-dataset", "example/synthetic", "--reference", "photos/"],
                       ["--images", "photos/"]):
            with tempfile.TemporaryDirectory() as folder:
                command = [sys.executable, str(SCRIPTS / "project.py"), "init", "--root", folder,
                           *source, "--count", "8", "--train-model", "act", "--train-model", "smolvla"]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                request = json.loads((Path(folder) / "request.json").read_text())
                self.assertEqual(request["training"]["models"], ["act", "smolvla"])
                self.assertTrue(request["deployment"]["requested"])
                self.assertFalse(request["deployment"]["physical_execution_authorized"])
                self.assertFalse(request["upload"]["enabled"])
                self.assertFalse((Path(folder) / "state.json").exists())

    def test_photo_only_does_not_infer_training_or_count(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(SCRIPTS / "project.py"), "init", "--root", folder,
                                     "--images", "photo.png"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads((Path(folder) / "request.json").read_text())
            self.assertEqual(request["authorized_limit"], 0)
            self.assertFalse(request["training"]["enabled"])


@unittest.skipUnless(HAS_DEPLOYMENT, "Optional torch/safetensors deployment dependencies")
class DeploymentTests(unittest.TestCase):
    def test_independent_affine_maps_preserve_tensor_contracts(self) -> None:
        mappings = validate_mapping(mapping_fixture())
        for feature, shape in (("observation.state", (4, 3)), ("action", (2, 7, 2))):
            scale, offset = mappings[feature]
            dimension = shape[-1]
            mean, std = torch.ones(dimension, dtype=torch.float64), torch.full((dimension,), .5, dtype=torch.float64)
            values = {f"{feature}.mean": mean, f"{feature}.std": std, f"{feature}.count": torch.tensor(10)}
            changed = transform_statistics(values, mappings)
            original = torch.arange(torch.tensor(shape).prod().item(), dtype=torch.float64).reshape(shape) / 10
            hardware = original * scale + offset
            normalized = (original - mean) / std
            torch.testing.assert_close((hardware - changed[f"{feature}.mean"]) / changed[f"{feature}.std"], normalized)
            torch.testing.assert_close(normalized * changed[f"{feature}.std"] + changed[f"{feature}.mean"], hardware)
            self.assertEqual(changed[f"{feature}.count"].item(), 10)

    def test_unsupported_mapping_and_statistics_fail(self) -> None:
        for bad in (0., -1., float("nan"), float("inf")):
            mapping = deepcopy(mapping_fixture())
            mapping["features"]["action"]["scale"][0] = bad
            with self.assertRaises(ValueError):
                validate_mapping(mapping)
        vectors = validate_mapping(mapping_fixture())
        with self.assertRaises(ValueError):
            transform_statistics({"action.mean": torch.ones(3), "action.std": torch.ones(3)}, vectors)
        with self.assertRaises(ValueError):
            transform_statistics({"action.mean": torch.ones(2), "action.std": torch.zeros(2)}, vectors)

    def test_checkpoint_preserves_weights_metadata_and_other_features(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "source", Path(folder) / "output"
            checkpoint_fixture(source)
            report = adapt_checkpoint(source, output, mapping_fixture())
            self.assertEqual((source / "model.safetensors").read_bytes(), (output / "model.safetensors").read_bytes())
            self.assertFalse(report["actual_runtime_verified"])
            self.assertFalse(report["real_task_success_verified"])
            for name in ("policy_preprocessor", "policy_postprocessor"):
                filename = name + ".safetensors"
                changed, original = load_file(str(output / filename)), load_file(str(source / filename))
                torch.testing.assert_close(changed["action.mean"], torch.tensor([4.25, -.25]))
                torch.testing.assert_close(changed["observation.state.mean"], torch.tensor([1.5, -4.25, 10.]))
                torch.testing.assert_close(changed["observation.images.camera.mean"], original["observation.images.camera.mean"])
                with safe_open(str(output / filename), framework="pt") as handle:
                    self.assertEqual(handle.metadata(), {"fixture": "synthetic"})
            with self.assertRaises(ValueError):
                adapt_checkpoint(output, Path(folder) / "double", mapping_fixture())
            with self.assertRaises(ValueError):
                adapt_checkpoint(source, output, mapping_fixture())

    def test_incomplete_or_unsupported_processor_does_not_create_output(self) -> None:
        for failure in ("missing", "mode", "shape"):
            with tempfile.TemporaryDirectory() as folder:
                source, output = Path(folder) / "source", Path(folder) / "output"
                checkpoint_fixture(source)
                path = source / "policy_postprocessor.json"
                config = json.loads(path.read_text())
                if failure == "missing":
                    config["steps"] = []
                elif failure == "mode":
                    config["steps"][0]["config"]["norm_map"]["ACTION"] = "MIN_MAX"
                else:
                    config["steps"][0]["config"]["features"]["action"]["shape"] = [6]
                path.write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    adapt_checkpoint(source, output, mapping_fixture())
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
