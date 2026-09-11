# Source intake and observability

Prefer demonstration video or a dataset episode plus multiview photos. Preserve recorded
motion when available and use other views to resolve the scene. The table below also
supports missing components; it is not a list of mandatory inputs.

Preserve a source manifest with dataset ID/local path, immutable revision, selected
episode, task, license, camera keys, source hashes and extraction commands. A video
path or camera name alone does not establish its identity: inspect frames and metadata
to distinguish fixed, wrist, stereo and moving cameras. Supplemental captures can show
different layouts or poses; mark that explicitly.

For LeRobot, start with `meta/info.json`, feature names/shapes, episode records and
task metadata. The helper supports the common v2 episode-file and v3 shared-shard
layouts. For other versions, inspect the installed official SDK before writing a
reader. Do not assume an episode index equals a video filename. V3 uses metadata to
locate episodes inside shared Parquet/video shards, including video time offsets.
See the [official v3 design](https://huggingface.co/docs/lerobot/lerobot-dataset-v3).

```bash
python scripts/source_episode.py --repo owner/dataset --episode 3 --output work/source
python scripts/source_episode.py --dataset /data/demo --episode 3 --output work/source
```

By default the tool resolves metadata and selected Parquet data. Add `--download-video`
to fetch the referenced camera shards; `--camera observation.images.side` selects one.
A shared file can necessarily contain other episodes: extraction must use the chosen
episode's offset/length. The helper records these bounds and does not silently trim
or resample. Pin the resolved repository commit even if the user supplied `main`.
Private downloads use HF's existing environment/cache credentials; never print tokens.
Redaction is opt-in: retain the original appearance unless the user explicitly requests
masking, pixelation or replacement. Ask about missing task inputs, not an unsolicited
privacy approval for ordinary windows/backgrounds.

Probe actual decoded count, dimensions, PTS and frame rate using ffprobe/PyAV. Detect
VFR, dropped frames and unsynchronized streams. Preserve original timestamps; if the
output needs CFR, document the resampling map. Extract sparse reference/contact frames
first. For phone HDR/HLG references, inspect color metadata and tone-map a working SDR
copy before taking texture/color measurements; preserve the original.

Create a source contract with:

- State names, dimensions and units; URDF/controller mapping; action names, units,
  semantics and latency. A normalized gripper signal is not automatically radians.
- Video stream identities, timestamps, intrinsics/distortion and calibration status.
- Demonstration phases and success criterion with supporting frames.
- Evidence provenance per surface/parameter: measured, fitted, inferred or unknown.

Input modes determine defensible outputs:

| Input | Output that can be supported |
| --- | --- |
| Video + measured joints + robot CAD | Calibrated FK reconstruction with preserved raw signals |
| Video + known robot, no joints | Fit/synthesize motion with reprojection and kinematic checks; label inferred, retain uncertainty |
| Video without identifiable robot/control contract | Visual reconstruction; actuator-level training labels remain unavailable until a robot mapping is supplied or explicitly chosen |
| Photos + task + identifiable robot, no demonstration | Estimate a metric scene and synthesize task motion; no measured trajectory exists |
| Optional orbit/images | Additional shape/appearance evidence; not extra task demonstrations |
| Text only for hidden surroundings | Plausible completion with an explicit uncertainty mask |

Do not stall visual reconstruction because joint labels are missing. Do not proceed to
claim measured robot demonstrations from arbitrary estimated motion. If a synthetic
control adapter is appropriate and authorized, implement it and clearly label its
provenance. Avoid generic pick/place assumptions for pouring, pushing, opening, mobile
navigation or bimanual tasks.

For model delivery, resolve the hardware state/action units and runtime camera contract at intake. Read [training-deployment.md](training-deployment.md) before choosing a training schema. Do not wait for the first failed rollout to discover that six simulator radians are five driver angles plus one calibrated gripper percentage.
