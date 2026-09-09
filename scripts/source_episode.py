"""Resolve one LeRobot v2/v3 episode; optional shared video downloads, no frame extraction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any

from project import checksum, write_json


class SourceStore:
    def __init__(self, root: Path | None, repo: str | None, revision: str, output: Path) -> None:
        self.root = root.resolve() if root else None
        self.repo = repo
        self.output = output
        if root:
            self.revision = None
            self.files = [p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file()]
        else:
            from huggingface_hub import HfApi
            info = HfApi().dataset_info(repo, revision=revision)
            self.revision = info.sha
            self.files = [item.rfilename for item in info.siblings]

    def get(self, relative: str) -> Path:
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or "\\" in relative:
            raise ValueError("Unsafe source metadata path")
        if self.root:
            result = (self.root / relative).resolve()
            if not result.is_relative_to(self.root):
                raise ValueError("Source path escapes dataset root")
            return result
        from huggingface_hub import hf_hub_download
        return Path(hf_hub_download(self.repo, relative, repo_type="dataset", revision=self.revision,
                                    cache_dir=self.output / ".cache/huggingface"))


def locate_files(info: dict[str, Any], episode: dict[str, Any], camera: str | None = None) -> dict[str, Any]:
    """Metadata -> shard names and episode-local/shared-video time bounds."""
    index = int(episode["episode_index"])
    version = info["codebase_version"]
    fps = float(info["fps"])
    if fps <= 0:
        raise ValueError("Invalid source FPS")
    if version.startswith("v2"):
        values = {"episode_index": index, "episode_chunk": index // int(info["chunks_size"])}
    elif version.startswith("v3"):
        values = {"chunk_index": int(episode["data/chunk_index"]), "file_index": int(episode["data/file_index"])}
    else:
        raise ValueError(f"Unsupported dataset version {version}; inspect the official SDK")
    data = info["data_path"].format(**values)
    keys = [key for key, feature in info["features"].items() if feature["dtype"] == "video"]
    if camera and camera not in keys:
        raise ValueError(f"Unknown video camera: {camera}; available: {keys}")
    videos: dict[str, Any] = {}
    for key in keys:
        if camera and key != camera:
            continue
        if version.startswith("v3"):
            video_values = {"chunk_index": int(episode[f"videos/{key}/chunk_index"]),
                            "file_index": int(episode[f"videos/{key}/file_index"]), "video_key": key}
            start = float(episode[f"videos/{key}/from_timestamp"])
            stop = float(episode[f"videos/{key}/to_timestamp"])
        else:
            video_values = {**values, "video_key": key}
            start, stop = 0.0, int(episode["length"]) / fps
        if start < 0 or stop <= start:
            raise ValueError("Invalid episode video interval")
        videos[key] = {"path": info["video_path"].format(**video_values), "from_timestamp": start,
                       "to_timestamp": stop, "length": int(episode["length"])}
    return {"data": data, "videos": videos}


def episode_record(store: SourceStore, info: dict[str, Any], index: int) -> tuple[dict[str, Any], Path]:
    if info["codebase_version"].startswith("v2"):
        path = store.get("meta/episodes.jsonl")
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                if record["episode_index"] == index:
                    return record, path
    elif info["codebase_version"].startswith("v3"):
        import pyarrow.compute as pc
        import pyarrow.parquet as pq
        for name in sorted(p for p in store.files if p.startswith("meta/episodes/") and p.endswith(".parquet")):
            path = store.get(name)
            table = pq.read_table(path)
            selected = table.filter(pc.equal(table["episode_index"], index))
            if len(selected) == 1:
                return selected.to_pylist()[0], path
            if len(selected) > 1:
                raise ValueError("Duplicate source episode record")
    else:
        raise ValueError("Unsupported source version; inspect the official SDK")
    raise ValueError(f"Episode {index} not found")


def inspect_episode(store: SourceStore, index: int, camera: str | None, download_video: bool) -> dict[str, Any]:
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    info_path = store.get("meta/info.json")
    info = json.loads(info_path.read_text(encoding="utf-8"))
    episode, metadata_path = episode_record(store, info, index)
    locations = locate_files(info, episode, camera)
    data_path = store.get(locations["data"])
    table = pq.read_table(data_path)
    selected = table.filter(pc.equal(table["episode_index"], index))
    if len(selected) != int(episode["length"]):
        raise ValueError("Resolved data shard does not cover the complete episode; adapt to this SDK's sharding before continuing")
    indices = selected["frame_index"].to_pylist()
    if indices != list(range(len(selected))):
        raise ValueError("Source frames are missing, duplicated or out of order")
    store.output.mkdir(parents=True, exist_ok=True)
    selected_path = store.output / "selected_episode.parquet"
    if selected_path.resolve() == data_path.resolve():
        raise ValueError("Output must not overwrite the source shard")
    pq.write_table(selected, selected_path)
    for details in locations["videos"].values():
        if download_video:
            local = store.get(details["path"])
            details.update(local_path=str(local), sha256=checksum(local))
    report = {"source": {"repo_id": store.repo, "local_root": str(store.root) if store.root else None,
                          "revision": store.revision, "episode_index": index},
              "codebase_version": info["codebase_version"], "fps": info["fps"], "frames": len(selected),
              "features": info["features"], "tasks": episode.get("tasks", []), "episode_metadata": episode,
              "resolved_files": locations, "selected_data": str(selected_path),
              "sha256": {"info": checksum(info_path), "episode_metadata": checksum(metadata_path),
                         "source_data_shard": checksum(data_path), "selected_data": checksum(selected_path)},
              "motion_status": "Raw fields preserved; robot mapping, units, camera identity and action semantics still require inspection",
              "frame_extraction_performed": False}
    write_json(store.output / "source_episode.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--repo")
    source.add_argument("--dataset", type=Path)
    parser.add_argument("--episode", type=int, required=True)
    parser.add_argument("--revision", default="main")
    parser.add_argument("--camera")
    parser.add_argument("--download-video", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.episode < 0:
        parser.error("Episode must be nonnegative")
    store = SourceStore(args.dataset, args.repo, args.revision, args.output.resolve())
    report = inspect_episode(store, args.episode, args.camera, args.download_video)
    print(json.dumps({"report": str(store.output / "source_episode.json"), "frames": report["frames"],
                      "cameras": list(report["resolved_files"]["videos"]), "revision": store.revision}, indent=2))


if __name__ == "__main__":
    main()
