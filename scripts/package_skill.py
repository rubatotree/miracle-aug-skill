"""Package code/docs and explicitly reviewed showcase images with a checksummed inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

TOP_FILES = {"SKILL.md", "README.md", "README.zh-CN.md", "LICENSE", ".gitignore", ".gitattributes", "requirements-source.txt"}
TOP_FOLDERS = {"agents", "references", "scripts", "tests", ".github"}
EXTENSIONS = {".py", ".c", ".md", ".yaml", ".yml", ".txt"}


def showcase_inventory(root: Path) -> set[Path]:
    directory = root / "assets/showcase"
    if not directory.exists():
        return set()
    release_path = directory / "release.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    if release.get("visual_review_passed") is not True:
        raise ValueError("Showcase images require a completed visual review")
    if release.get("redaction_requested") and release.get("source_pixels_removed") is not True:
        raise ValueError("Requested showcase redaction has not passed")
    result = {release_path, directory / "README.md"}
    for name, expected in release["files"].items():
        path = directory / name
        if Path(name).name != name or "\\" in name or path.suffix.lower() not in {".jpg", ".png", ".webp"}:
            raise ValueError("Only explicitly listed showcase images may enter the release")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Showcase image changed after review")
        result.add(path)
    return result


def inventory(root: Path) -> list[Path]:
    showcase = showcase_inventory(root)
    paths = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(root)
        if relative.as_posix() in TOP_FILES or (relative.parts[0] in TOP_FOLDERS and path.suffix in EXTENSIONS) or path in showcase:
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("Release must not traverse linked external files")
            if path.suffix.lower() in {".jpg", ".png", ".webp"}:
                paths.append(path)
                continue
            text = path.read_text(encoding="utf-8")
            if re.search(r"\bhf_[A-Za-z0-9]{20,}\b|\btsk_[A-Za-z0-9]{16,}\b|(?m:^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----$)", text):
                raise ValueError(f"Possible credential in {relative}")
            if path.suffix == ".md":
                for target in re.findall(r"\]\(([^)]+)\)", text):
                    target = target.strip("<>").split("#")[0]
                    if not target or "://" in target:
                        continue
                    resolved = (path.parent / target).resolve()
                    if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                        raise ValueError(f"Broken or external local link in {relative}: {target}")
            paths.append(path)
    if not TOP_FILES.issubset({p.relative_to(root).as_posix() for p in paths}):
        raise ValueError("Missing required release files")
    included = {p.resolve() for p in paths}
    for path in paths:
        if path.suffix != ".md":
            continue
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = target.strip("<>").split("#")[0]
            if target and "://" not in target and (path.parent / target).resolve() not in included:
                raise ValueError(f"Linked file is not in the release inventory: {target}")
    return paths


def package(root: Path, output: Path) -> dict[str, object]:
    paths = inventory(root)
    manifest = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".partial.zip")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            entry = zipfile.ZipInfo("miracleaug/" + path.relative_to(root).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, path.read_bytes())
        entry = zipfile.ZipInfo("miracleaug/RELEASE_MANIFEST.json", date_time=(2026, 1, 1, 0, 0, 0))
        archive.writestr(entry, json.dumps({"name": "MiracleAug", "files": manifest}, indent=2))
    temporary.replace(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return {"archive": str(output), "sha256": digest, "files": len(paths), "bytes": output.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package(Path(__file__).resolve().parents[1], args.output.resolve()), indent=2))


if __name__ == "__main__":
    main()
