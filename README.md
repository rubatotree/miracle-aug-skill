# MiracleAug

Demonstration and multiview references → reconstructed scene → augmented data → rollout policy.

English · [简体中文](README.zh-CN.md)

MiracleAug is an agent skill for turning a robot demonstration and multiview references
into an editable Blender scene, augmented demonstrations and, when requested, trained
LeRobot policies with verified deployment units, processors and rollout commands.
It is designed for GPT-6 Astra or a model with equivalent or stronger visual, spatial
and coding capabilities.

The preferred input is a demonstration video or dataset episode plus multiview photos.
Missing photos, joint logs or demonstration video are supported: the agent proceeds
with available evidence, estimating or synthesizing missing quantities explicitly.
It saves a scene checkpoint, constructs complete task seeds, generates the requested
data, and continues through authorized local training and model publication. Training
and upload can run concurrently from one frozen local snapshot.

## Historical demonstration-based showcase

![MiracleAug reconstructed scene, reverse view, glass, alternate toy, colored lighting and metal material](assets/showcase/overview.jpg)

Actual Blender renders from the completed tabletop reconstruction: the calibrated
scene, a reverse camera, glass and metal materials, an alternate toy, and colored
lighting. Each tile is rendered with Cycles at 640 × 480, with a 128-sample limit.
No original camera frames or generated illustrations are used in this gallery.

The exterior is replaced with an opaque synthetic mosaic **at this scene owner's
request**. MiracleAug preserves scene appearance by default; redaction is applied
only when the user explicitly requests it. The same request covers reflections,
transmission and packed source images.

![Three frames showing rest, transport and completed placement](assets/showcase/task-sequence.jpg)

The same calibrated demonstration at frames 0, 240 and 427: rest, transport and the
object remaining inside the cup after retraction. These are selected frames from
full-length trajectory validation, not a claim that the long dataset batch has finished.

![Cycles and Eevee renders at the same camera and demonstration time](assets/showcase/renderer-comparison.jpg)

Matched camera and task time: Cycles with a 128-sample limit and Eevee with 64 samples.
Both use the same reconstructed scene and trajectory. Engine settings and quality
labels accompany the data; training weights are configurable and default to one.

See [showcase provenance and attribution](assets/showcase/README.md) for render settings,
privacy scope and asset sources. These images demonstrate scene results. The separate
64-Cycles / 1,216-Eevee production batch was still running when this gallery was prepared;
complete dataset upload and improved policy generalization are not claimed here.

## What the skill carries through

- Metric, separated geometry; CAD/URDF robot kinematics; calibrated cameras and motion;
  source-view overlays and checks from new viewpoints.
- Weak and strong camera, lighting, material, environment, object and trajectory
  variations, with replanning when a change affects task contact or reachability.
- Exact accepted quotas, seeded candidates, same-category replacements, immutable
  checkpoints and resumable server execution.
- Native dataset validation, synchronized inspection videos and JSON, control semantics,
  renderer labels, seed lineage and explicit limitations.
- Reusable motion/layout seeds, mixed observation variants, asynchronous preparation,
  rendering, export, training and verified uploads with persistent progress.
- ACT/SmolVLA training, both saved processors, explicit hardware units, sequential
  runtime checks and model-specific rollout diagnostics.

Unobserved surfaces remain labelled as inferred. When input contains video but no
joint/control data, estimated motion is identified as inferred or synthesized;
it is never presented as recorded action ground truth. Dataset validity and policy
generalization are evaluated separately.

## Use MiracleAug

Place this directory at `~/.codex/skills/miracleaug` or in your agent's compatible
skill directory. The entry point is [SKILL.md](SKILL.md). The skill works with your own
inputs and does not require the private source dataset or scene used in the gallery.

```bash
git clone https://github.com/rubatotree/miracle-aug-skill.git ~/.codex/skills/miracleaug
```

Example request:

> Use $miracleaug to reconstruct episode 3 of the Hugging Face dataset owner/demo.
> Use the supplied multiview photos as geometry/appearance references. Save a Blender scene
> checkpoint, then generate 100 accepted demonstrations on my Ubuntu GPU server:
> 20 Cycles and 80 Eevee. Emphasize strong lighting, material and camera variations.
> Export LeRobot data, per-episode videos and JSON. Train ACT and SmolVLA on the local
> data, and publish data/models to my specified repositories. Include rollout commands
> for my robot and cameras; use at most the GPU allowance specified for this project.

A single `demo.mp4`, a dataset episode, or only photos plus a task can also start the
workflow. Photo-only task motion is synthetic, never reported as recorded ground truth.
You can request reconstruction only. To redact a scene, add an explicit instruction
such as “pixelate the exterior before rendering or sharing.” Otherwise no redaction
is performed. The agent inspects available metadata before asking for missing inputs.

## Citation

The most recent tagged release is v0.1.3. Cite that fixed version when it is the
version used in research; `main` contains subsequent development updates.
See [CITATION.cff](CITATION.cff) or [CITATION.bib](CITATION.bib).

## Tools and verification

The package includes a selected-episode reader, a finite quota/evidence ledger, a
frame-contract validator, a positive-affine policy-unit adapter, platform-specific
headless EGL support, and synthetic tests.
The agent implements the actual robot/task adapter; this is not a pretrained universal
inverse-rendering or action-recovery model.

The source/ledger/frame helpers use Python 3.10+ with optional source dependencies in
[requirements-source.txt](requirements-source.txt). Unit adaptation uses PyTorch and
safetensors; see [requirements-deployment.txt](requirements-deployment.txt) and reuse
the pinned training environment.
Blender and the native dataset SDK are selected and recorded for each generated project.

```bash
python -m unittest discover -s tests -v
python scripts/package_skill.py --output dist/MiracleAug-skill.zip
```

Tests cover quota/refill/resume behavior, variable state/action dimensions, multiple
cameras, timestamp/action alignment and LeRobot v2/v3 episode resolution. See
[validation scope](references/validation.md) for the evidence and remaining limitations.
Synthetic tests need no GPU, private data or access token. Optional integration tests
run when their dependencies are installed. A deployment artifact is not proof of real
task success; the photo-driven case reached real grasp/transport but release remained
unresolved at this update. See [case lessons](references/case-lessons.md).

This directory can serve as a standalone GitHub repository. Releases use an explicit
file allowlist, checked local links and SHA-256 manifests; only reviewed showcase
images may accompany the code. Original videos, scene files, caches and credentials
are not included. MIT covers the original code and documentation; third-party asset
licenses and showcase attribution are documented separately.
