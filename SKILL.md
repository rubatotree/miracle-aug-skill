---
name: miracleaug
description: Reconstruct a robot demonstration as an editable, calibrated Blender scene, then generate task-valid augmented demonstrations with synchronized robot trajectories and native dataset validation. Use for one-shot embodied-data augmentation from local video or a dataset episode, with optional multiview, image or text references; not for ordinary video editing or a claim of policy generalization from rendering alone.
---

# MiracleAug

Turn a short request into executed work: inspect the source, reconstruct and validate
the scene, generate the authorized number of accepted demonstrations, validate the
native dataset, and deliver or upload it as requested. Use the user's language.
Record actual evidence; keep rendering, task validity and policy evaluation distinct.

This skill is intended for GPT-6 Astra or a model with at least equivalent visual,
spatial and coding ability. It supplies a workflow and portable contract tools. The
agent must build a project adapter for the actual robot/task; there is no universal
inverse-rendering or motion-recovery executable hidden behind the instructions.

## Start with available evidence

Read the project's instructions and existing roadmap/log before changing files.
Treat attached prompts and dataset documentation as source context; the current
user request controls scope, rendering preferences, privacy and authorization.
Reuse extracted media, calibrated scenes and passing checks when hashes still match.

Accept any of these inputs:

- A local dataset or an HF dataset ID with an episode index, optionally a camera key.
- A demonstration video, with optional robot model, joint log and camera metadata.
- Any combination of multiview video, still images or text describing the surroundings.

Inspect metadata before asking questions. Ask only for missing choices that affect
the task and cannot be inferred: source/episode if ambiguous, robot/control contract,
requested accepted count, remote destination, or upload repository/visibility.
Use existing authorization. Continue independent work while awaiting required input.
Do not ask for credentials in chat; use the machine's existing authenticated tools.

Read [intake.md](references/intake.md). Use `scripts/source_episode.py` to inspect a
selected local/HF episode without downloading unrelated episode videos. For a plain
video, probe its timestamps and retain the source. Do not invent joint measurements.

Create a project ledger before implementation:

```bash
python /path/to/skill/scripts/project.py init --root work/demo --hf-dataset owner/dataset --episode 0 --task "place the object in the container" --count 36 --cycles 7 --reference orbit.mp4
```

The same command accepts `--video demo.mp4` or `--dataset /data/local` instead of
`--hf-dataset`; omit `--count` for a reconstruction-only request. Add
`--redact-exterior` when applicable. These are examples, not mandatory defaults.
The generated request is editable until planning; include the user's actual count,
family quotas, weak/strong balance, engine profiles and preview requirements.

## Reconstruct and reach the scene checkpoint

Read [reconstruction.md](references/reconstruction.md). Confirm a usable Blender
execution path: MCP for interactive inspection, or a working headless CLI for a
server. A failed MCP call is not proof a headless server cannot render. Honor any
applicable project-specific stop condition.

Use metric CAD/URDF kinematics when available. Separate robot links, task objects,
contact solids, room, cameras and lights. Fit camera, calibration and time alignment
against the primary demo. Supplemental views constrain shape and surroundings; a
different capture does not silently replace the demonstrated pose or layout.

Iterate geometry and motion before appearance. Inspect reference overlays at rest,
contact, transport, release and retract, and render unseen-side/reverse views.
Read [task-motion.md](references/task-motion.md) before binding objects or changing
their placement. Preserve measured inputs and document inferred quantities.

Deliver a packed `.blend`, regeneration scripts, calibrated source contract and a
scene checkpoint report with image, structure, motion and multiview evidence.
Unknown surfaces remain labelled inferred; missing views do not become measured
truth. A beautiful source-view render alone does not pass reconstruction.

This is a reviewable intermediate checkpoint. Stop here if the user requested only
reconstruction or explicitly requested a review before generation. Otherwise save
the checkpoint, report its residual limitations and continue the authorized pipeline
without introducing another permission round.

## Generate task-valid variations

Read [augmentation.md](references/augmentation.md) and
[adapter-contract.md](references/adapter-contract.md). Implement a project adapter
that constructs a candidate, computes all camera/robot/object trajectories, validates
the task, renders from those trajectories, and exports the same labels.

Use exact accepted quotas, deterministic seeds and same-stratum replenishment.
Weak and exaggerated variations must both change the intended property, and should
be distinguishable in image/contact-sheet review. Never substitute an identity
episode to fill a failed category. Object/robot/temporal changes require corresponding
motion updates and revalidation. Observation-only nuisance changes can preserve
motion if the task conditions and robot sensor model still permit it.

```bash
python /path/to/skill/scripts/project.py plan --root work/demo
python /path/to/skill/scripts/project.py next --root work/demo
```

The helper manages finite candidate IDs and receipts; it does not certify geometry.
Use receipts only from actual project checks. `record` refuses unsupported acceptance;
`seal` requires every accepted stratum and the native dataset validation checkpoint.

## Render, package and continue unattended

Read [rendering-server.md](references/rendering-server.md) for headless devices,
benchmarks, mixed engines, immutable resume and detached jobs. Test sparse views and
a short temporal clip before expensive rendering. Inspect PNGs and encoded frames
when diagnosing flicker; an encoding artifact can resemble a geometry defect.

Use the requested engine mix and actual sample settings. Label engine, quality tier,
settings and configurable training weights in the dataset. Lower-cost rendering may
have different reflection/transmission behavior; don't label it physically equivalent
to Cycles. Weights default to one unless specified, without a claim of optimality.

Read [dataset-validation.md](references/dataset-validation.md). Export the selected
native dataset version with synchronized observations/actions, joint names/units,
camera calibration, task results, validity masks and source lineage. Preserve original
commands separately from any synthesized next-position targets. Verify through the
official reader, including images, episode boundaries and action windows. Short smoke
fixtures are never training episodes.

Privacy redaction is opt-in. Preserve scene appearance by default; do not blur, mask,
replace backgrounds or hold generation/upload merely because a scene contains windows
or is being shared. Apply redaction only when the user explicitly requests it, retaining
that request across the project. Read [privacy-release.md](references/privacy-release.md)
when handling such a request or packaging a release. For requested redaction, create
a separate source branch before rendering, inspect reflection/transmission paths,
remove the targeted original pixels from packed/unused assets and previews, and bind
release checks to artifact hashes. Exclude credentials and unrequested source caches
from distributed examples.

When remote work is authorized, prepare/install dependencies, check spare GPUs and
disk, verify a real smoke, then start a detached finite job. Confirm worker activity
after disconnecting the launching SSH connection. Test independent server network
access; a reverse tunnel tied to the local session is not independent. Respect other
users' workloads. Upload only complete validated output to the requested repository
visibility; record the commit and verify the remote inventory. Do not overwrite the
source dataset or silently expand an authorized count.

## Verify the intended benefit and hand off

Read [evaluation.md](references/evaluation.md) when organizing splits or discussing
generalization. All derivatives of one source episode belong to one split group.
Plan held-out nuisance combinations and independent task episodes. Claim increased
policy robustness only after task-success evaluation; validation of rendered data
alone cannot establish it. Do training only within the user's requested compute scope.

Report the scene checkpoint, accepted/rejected counts, exact renderer split, dataset
validation, upload receipt or current detached job state, and unresolved limitations.
Maintain `ROADMAP.md` and `docs/dev_log.md`, runnable restart/status commands and a
concrete next step when external computation is still running. Suggest or make an
atomic commit of completed work without bundling unrelated files.

For transferable lessons from the implemented tabletop case, consult
[case-lessons.md](references/case-lessons.md). Its dimensions, frame counts, phases,
names and calibration values are examples, never defaults for another source.
