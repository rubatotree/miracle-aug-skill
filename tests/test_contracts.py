"""Fully synthetic behavioral fixtures; no private images, robot assets or credentials."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import project
from source_episode import SourceStore, inspect_episode, locate_files
from validate_episode import validate
from package_skill import package, showcase_inventory


def make_project(root: Path, count: int = 7, cycles: int = 2, private: bool = False) -> None:
    project.initialize(argparse.Namespace(root=root, count=count, cycles=cycles, hf_dataset=None, dataset=None,
                       video="synthetic.mp4", episode=0, task="Push a synthetic block", reference=[], seed=17,
                       redact_exterior=private))
    (root / "synthetic_evidence.txt").write_text("A numeric fixture; not a validated Blender scene.")
    report = {"passed": True, "checks": dict.fromkeys(project.CHECKS["scene"], True), "artifacts": ["synthetic_evidence.txt"]}
    project.write_json(root / "checks/scene.json", report)
    project.checkpoint(root, "scene", "checks/scene.json")


def receipt(root: Path, candidate: str, outcome: str = "accepted", privacy: bool = False) -> str:
    record = {"candidate_id": candidate, "plan_sha256": project.checksum(root / "plan.json"), "outcome": outcome,
              "checks": dict.fromkeys(("geometry", "task_success", "visibility", "render_complete", "labels"), True),
              "reason": "Synthetic rejected constraint" if outcome == "rejected" else None,
              "artifacts": ["synthetic_evidence.txt"]}
    if privacy:
        record["checks"]["privacy"] = True
    relative = f"checks/{candidate}.json"
    project.write_json(root / relative, record)
    return relative


class LedgerTests(unittest.TestCase):
    def test_exact_large_split_determinism_and_authorized_cap(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            make_project(root, 1280, 64)
            first = project.create_plan(root)
            self.assertEqual(first, project.create_plan(root))
            self.assertEqual(sum(s["required"] for key, s in first["strata"].items() if key.endswith("/CYCLES")), 64)
            self.assertEqual(sum(s["required"] for key, s in first["strata"].items() if key.endswith("/BLENDER_EEVEE")), 1216)
            self.assertEqual(len(first["candidates"]), 1280 * 12)
            request = project.read_json(root / "request.json")
            request["authorized_limit"] = 1279
            with self.assertRaisesRegex(ValueError, "authorized"):
                project.validate_request(request)

    def test_same_stratum_refill_resume_and_seal(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            make_project(root)
            project.create_plan(root)
            rejected = project.pending(root)[0]
            path = receipt(root, rejected["id"], "rejected")
            project.record_receipt(root, path)
            replacement = next(c for c in project.pending(root) if c["stratum"] == rejected["stratum"])
            self.assertNotEqual(rejected["id"], replacement["id"])
            accepted = []
            while project.pending(root):
                for candidate in project.pending(root):
                    path = receipt(root, candidate["id"])
                    project.record_receipt(root, path)
                    project.record_receipt(root, path)  # Resume is idempotent.
                    accepted.append(candidate["id"])
            self.assertEqual(len(accepted), 7)
            report = {"passed": True, "checks": dict.fromkeys(project.CHECKS["dataset"], True),
                      "artifacts": ["synthetic_evidence.txt"], "accepted_candidate_ids": accepted}
            project.write_json(root / "checks/dataset.json", report)
            project.checkpoint(root, "dataset", "checks/dataset.json")
            self.assertEqual(project.seal(root)["accepted"], 7)
            self.assertEqual(project.pending(root), [])
            self.assertNotIn(rejected["id"], accepted)
            extra = next(c for c in project.load_plan(root)["candidates"] if c["id"] not in accepted and c["id"] != rejected["id"])
            with self.assertRaisesRegex(ValueError, "authorized"):
                project.record_receipt(root, receipt(root, extra["id"]))

    def test_changed_evidence_and_request_invalidate_resume(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            make_project(root)
            project.create_plan(root)
            (root / "synthetic_evidence.txt").write_text("Changed after scene checkpoint")
            with self.assertRaisesRegex(ValueError, "artifact changed"):
                project.pending(root)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            make_project(root)
            project.create_plan(root)
            request = project.read_json(root / "request.json")
            request["seed"] += 1
            project.write_json(root / "request.json", request)
            with self.assertRaisesRegex(ValueError, "request changed"):
                project.pending(root)

    def test_privacy_and_preview_do_not_accept_without_checks(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            make_project(root, private=True)
            project.create_plan(root)
            candidate = project.pending(root)[0]["id"]
            with self.assertRaisesRegex(ValueError, "Acceptance"):
                project.record_receipt(root, receipt(root, candidate))
            path = receipt(root, candidate, privacy=True)
            content = project.read_json(root / path)
            content["checks"]["render_complete"] = False
            project.write_json(root / path, content)
            with self.assertRaisesRegex(ValueError, "Acceptance"):
                project.record_receipt(root, path)

    def test_exhaustion_stops_without_extra_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            make_project(root, 1, 1)
            request = project.read_json(root / "request.json")
            request["attempts_per_episode"] = 1
            project.write_json(root / "request.json", request)
            project.checkpoint(root, "scene", "checks/scene.json")
            project.create_plan(root)
            candidate = project.pending(root)[0]["id"]
            project.record_receipt(root, receipt(root, candidate, "rejected"))
            with self.assertRaisesRegex(ValueError, "exhausted"):
                project.pending(root)

    def test_paths_cannot_escape_project(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "inside"):
                project.inside(Path(folder), "../outside.txt")

    def test_cli_scene_only_init_does_not_authorize_generation(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(SCRIPTS / "project.py"), "init", "--root", folder,
                                     "--video", "synthetic.mp4"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            request = project.read_json(Path(folder) / "request.json")
            self.assertEqual(request["authorized_limit"], 0)
            self.assertFalse(request["privacy"]["redact_exterior"])
            with self.assertRaises(ValueError):
                project.validate_request(request)


def frame_fixture(length: int, dimension: int, semantics: str = "next_position_target") -> tuple[dict, list[dict]]:
    schema = {"state_names": [f"joint{i}" for i in range(dimension)], "action_names": [f"joint{i}" for i in range(dimension)],
              "state_units": ["rad"] * dimension, "action_units": ["rad"] * dimension, "action_semantics": semantics,
              "fps": 25, "cameras": ["fixed", "wrist"], "privacy_required": True}
    rows = []
    for index in range(length):
        camera = {"intrinsics": [[400, 0, 320], [0, 400, 240], [0, 0, 1]],
                  "world_from_camera": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], "timestamp": index / 25}
        rows.append({"frame_index": index, "timestamp": index / 25, "observation.state": [index * .1] * dimension,
                     "action": [min(index + 1, length - 1) * .1] * dimension, "action_valid": index + 1 < length,
                     "cameras": {"fixed": copy.deepcopy(camera), "wrist": copy.deepcopy(camera)},
                     "render.engine": "BLENDER_EEVEE", "training.sample_weight": 1.0, "privacy.redacted": True})
    return schema, rows


class FrameContractTests(unittest.TestCase):
    def test_variable_dof_length_and_two_cameras(self) -> None:
        for length, dimension in ((3, 7), (11, 2), (1, 8)):
            schema, rows = frame_fixture(length, dimension)
            result = validate(schema, rows)
            self.assertEqual(result["frames"], length)
            self.assertEqual(result["state_dimension"], dimension)
            self.assertFalse(result["geometry_checked"])

    def test_recorded_commands_are_not_assumed_next_state(self) -> None:
        schema, rows = frame_fixture(4, 7, "recorded_command")
        schema["action_names"] = ["grip_velocity"]
        schema["action_units"] = ["m/s"]
        for row in rows:
            row["action"] = [0.03]
            row["action_valid"] = True
        self.assertTrue(validate(schema, rows)["passed"])

    def test_misalignment_privacy_and_nonfinite_camera_fail(self) -> None:
        schema, source = frame_fixture(4, 7)
        for mutation in ("action", "time", "privacy", "camera", "reflection"):
            rows = copy.deepcopy(source)
            if mutation == "action": rows[0]["action"][0] += .2
            if mutation == "time": rows[1]["timestamp"] = rows[0]["timestamp"]
            if mutation == "privacy": rows[0]["privacy.redacted"] = False
            if mutation == "camera": rows[0]["cameras"]["fixed"]["timestamp"] = float("nan")
            if mutation == "reflection": rows[0]["cameras"]["fixed"]["world_from_camera"][0][0] = -1
            with self.assertRaises(ValueError, msg=mutation):
                validate(schema, rows)


class SourceTests(unittest.TestCase):
    def test_v3_shared_shard_offsets_and_named_camera(self) -> None:
        info = {"codebase_version": "v3.0", "fps": 25, "features": {"observation.images.wrist": {"dtype": "video"}},
                "data_path": "data/chunk-{chunk_index:03d}/file-{file_index:03d}.parquet",
                "video_path": "videos/{video_key}/chunk-{chunk_index:03d}/file-{file_index:03d}.mp4"}
        episode = {"episode_index": 37, "length": 3, "data/chunk_index": 2, "data/file_index": 4,
                   "videos/observation.images.wrist/chunk_index": 1, "videos/observation.images.wrist/file_index": 8,
                   "videos/observation.images.wrist/from_timestamp": 12.5, "videos/observation.images.wrist/to_timestamp": 12.62}
        result = locate_files(info, episode, "observation.images.wrist")
        self.assertEqual(result["data"], "data/chunk-002/file-004.parquet")
        self.assertEqual(result["videos"]["observation.images.wrist"]["from_timestamp"], 12.5)
        self.assertIn("file-008", result["videos"]["observation.images.wrist"]["path"])
        with self.assertRaisesRegex(ValueError, "Unknown"):
            locate_files(info, episode, "front")

    @unittest.skipUnless(importlib.util.find_spec("pyarrow"), "Optional PyArrow source integration dependency")
    def test_local_v2_and_v3_selected_episode_preserves_numeric_rows(self) -> None:
        import pyarrow as pa
        import pyarrow.parquet as pq
        for version in ("v2.1", "v3.0"):
            with tempfile.TemporaryDirectory() as folder:
                root, output = Path(folder) / "source", Path(folder) / "selected"
                info = {"codebase_version": version, "fps": 25, "chunks_size": 1000,
                        "features": {"observation.state": {"dtype": "float32", "shape": [7]}}}
                episodes = [{"episode_index": i, "length": i + 2, "tasks": ["Push the block"],
                             "data/chunk_index": 0, "data/file_index": 0} for i in (0, 1)]
                rows = [{"episode_index": i, "frame_index": j, "timestamp": j / 25, "observation.state": [float(j)] * 7}
                        for i in (0, 1) for j in range(i + 2)]
                if version.startswith("v3"):
                    info["data_path"] = "data/chunk-{chunk_index:03d}/file-{file_index:03d}.parquet"
                    metadata = root / "meta/episodes/chunk-000/file-000.parquet"
                    metadata.parent.mkdir(parents=True)
                    pq.write_table(pa.Table.from_pylist(episodes), metadata)
                    data = root / "data/chunk-000/file-000.parquet"
                    data.parent.mkdir(parents=True)
                    pq.write_table(pa.Table.from_pylist(rows), data)
                else:
                    info["data_path"] = "data/chunk-{episode_chunk:03d}/episode_{episode_index:06d}.parquet"
                    (root / "meta").mkdir(parents=True)
                    (root / "meta/episodes.jsonl").write_text("".join(json.dumps(e) + "\n" for e in episodes))
                    for i in (0, 1):
                        data = root / f"data/chunk-000/episode_{i:06d}.parquet"
                        data.parent.mkdir(parents=True, exist_ok=True)
                        pq.write_table(pa.Table.from_pylist([r for r in rows if r["episode_index"] == i]), data)
                project.write_json(root / "meta/info.json", info)
                report = inspect_episode(SourceStore(root, None, "main", output), 1, None, False)
                self.assertEqual(report["frames"], 3)
                self.assertEqual(pq.read_table(output / "selected_episode.parquet").to_pylist(), [r for r in rows if r["episode_index"] == 1])


class ReleaseTests(unittest.TestCase):
    def test_release_is_deterministic_and_media_is_explicitly_reviewed(self) -> None:
        import zipfile
        with tempfile.TemporaryDirectory() as folder:
            first = package(SCRIPTS.parent, Path(folder) / "first.zip")
            second = package(SCRIPTS.parent, Path(folder) / "second.zip")
            self.assertEqual(first["sha256"], second["sha256"])
            with zipfile.ZipFile(first["archive"]) as archive:
                names = archive.namelist()
                self.assertIn("miracleaug/SKILL.md", names)
                self.assertIn("miracleaug/RELEASE_MANIFEST.json", names)
                self.assertFalse(any(name.endswith((".blend", ".mp4", ".env", ".pyc")) for name in names))
                release = json.loads(archive.read("miracleaug/assets/showcase/release.json"))
                actual_images = {Path(name).name for name in names if name.endswith((".jpg", ".png", ".webp"))}
                self.assertEqual(actual_images, set(release["files"]))

    def test_media_redaction_is_only_required_when_requested(self) -> None:
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            media = root / "assets/showcase"
            media.mkdir(parents=True)
            (media / "example.jpg").write_bytes(b"Synthetic hash fixture, not an image decoder test")
            (media / "README.md").write_text("Synthetic fixture")
            release = {"visual_review_passed": True, "redaction_requested": False, "source_pixels_removed": False,
                       "files": {"example.jpg": hashlib.sha256((media / "example.jpg").read_bytes()).hexdigest()}}
            project.write_json(media / "release.json", release)
            self.assertEqual(len(showcase_inventory(root)), 3)
            release["redaction_requested"] = True
            project.write_json(media / "release.json", release)
            with self.assertRaisesRegex(ValueError, "redaction"):
                showcase_inventory(root)
            release.update(redaction_requested=False)
            project.write_json(media / "release.json", release)
            (media / "example.jpg").write_bytes(b"Changed after review")
            with self.assertRaisesRegex(ValueError, "changed"):
                showcase_inventory(root)


if __name__ == "__main__":
    unittest.main()
