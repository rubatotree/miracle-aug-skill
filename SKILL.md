---
name: miracleaug
description: Augment robot demonstrations using demonstration video or a dataset episode plus multiview photos, reconstructing editable scenes and task-valid motion through native data and optional trained rollout policies. Also handles missing views, missing joint logs or photo-only task synthesis with explicit inference provenance.
---

# MiracleAug

Carry a simple source-and-task request through executed work: editable reconstruction,
observable task motion, augmented native data and, when requested, trained policies
with a reproducible rollout command. Use the user's language. A dataset-only request
does not authorize training; model delivery does not authorize operating remote hardware.
Continue already authorized stages without repeated permission rounds.

This skill supplies an engineering workflow and portable helpers, not a universal
inverse renderer, task planner or pretrained robot controller. Implement the actual
scene/robot/task adapter. State separately what was visually reviewed, physically
simulated, inherited from a seed, checked numerically, trained and tested on hardware.

## Start from evidence and the requested endpoint

Read project instructions, roadmap and logs. Inspect local files, source metadata,
installed SDK/driver code, authenticated caches and available compute before asking
for missing inputs. Reuse matching cached assets and datasets. Do not ask for secrets.

The primary workflow uses demonstration video or a local/HF dataset episode together
with multiview photos. Preserve measured motion and use photos to constrain geometry
and appearance. Missing photos, joint logs or even the demonstration are supported
fallbacks; select the evidence-appropriate path instead of demanding the complete set.
Supplemental views do not create measured motion.
With still images, synthesize an expert trajectory and label it synthetic. With an
unknown robot, proceed on appearance while resolving the actuator contract; do not
invent measured actions. “Zero-shot” must say zero of what: a photo-conditioned dataset
can use robot CAD, task knowledge, simulator tuning and pretrained model weights.

Read [intake.md](references/intake.md) and
[end-to-end.md](references/end-to-end.md). Recover the robot, cameras, task success,
count, compute scope, model choices and destination from context where possible.
Ask once for a missing decision that changes scope or validity; continue independent work. Use bounded,
recorded defaults for routine details; historical case counts are not new authorization.

Create/update `ROADMAP.md` and `docs/dev_log.md` before implementation. For example:

```bash
python /path/to/skill/scripts/project.py init --root work/task \
  --hf-dataset owner/demo --episode 0 --reference photos/ \
  --task "Find the toy and place it in the cup" \
  --count 100 --cycles 10 --train-model act --train-model smolvla
```

For a photo-only fallback use `--images photos/`, a file/directory reference rather
than an image-to-motion executable. The helper also accepts `--video`, `--dataset` or
`--hf-dataset`; use `source_episode.py` for a
selected dataset episode. Omit count for reconstruction only and model flags for
dataset only. Edit inferred family quotas, camera roles, quality profiles and delivery
settings to match the actual request before planning. Training flags record scope;
they do not launch jobs. Remote destinations and physical rollout remain separate.

## Reconstruct an editable, credible scene

Read [reconstruction.md](references/reconstruction.md). Use metric CAD/URDF and an
independent FK implementation. Separate robot links, task solids, visible surfaces,
room, cameras and lights. Fit camera/layout from several landmarks/views before
appearance. A name such as `front` does not establish whether a camera is wrist-mounted.

Inspect geometry and semantics object by object and in the composed scene. Prioritize
large visible surfaces, recognizable faces and task markers. Build material-scale
texture and fabric structure; flat rough shading alone often still looks plastic.
Verify decals against each relevant view, including cylindrical wrap/handle orientation.
Freeze accepted artwork as one versioned asset used by previews and production.

Render reference overlays and novel-view extrema. Mark hidden geometry and estimated
sizes as inferred. Correct visual assets can be independent of collision proxies, but
their contact geometry and deformation must correspond. Save a packed `.blend`, rebuild
scripts, hashes and residuals. A saved checkpoint is an intermediate deliverable, not
an automatic pause; stop only when requested or when a genuine required input blocks it.

## Build observable, complete task seeds

Read [task-motion.md](references/task-motion.md). Define success from the request:
for example, resting across a rim can qualify when allowed, provided the object stays
there after release and retraction. Do not silently demand perfect insertion or zero
vibration. Conversely, holding an object above the destination is not completed placing.

If target visibility is initially absent, generate a target-independent search motion,
then acquire actual camera evidence before target-dependent approach. Simulator poses
may support a synthetic expert but must not leak into policy observations or be called
an RGB-only planner. Check camera mount, cable constraints if relevant, joint reach,
contact transitions, commanded versus achieved motion, release and post-release rest.

Get a small set of complete seeds before broad sampling. Investigate localized contact
or numerical failures with small reproducible probes before changing the entire solver.
Do not treat IK convergence, mesh parenting or a visually plausible clip as physical
success. Match the simulated command hold/interpolation to the intended controller.

## Produce useful coverage with reusable motion

Read [augmentation.md](references/augmentation.md) and
[adapter-contract.md](references/adapter-contract.md). Factor expensive motion/layout
seeds from cheap camera/appearance variants. Label full physics, inherited contact and
kinematic checks separately; rendering many textures does not multiply independent seeds.

For placement tasks, diversify the full movable layout, target-to-container direction
and distance, target yaw, and distractor count where permitted. Preserve semantic task
identity. Most samples should combine meaningful nuisance axes when that is the goal;
use single-axis samples to diagnose coverage. Separate ordinary camera-placement error
from rare opposite/extreme views and material/light intensity. Store numerical ranges
and coordinate definitions rather than relying on “weak”, “far” or “left”.

Review representative seeds and changed mechanisms; do not repeat costly physics or
visual review for every appearance variant. Retain cheap per-episode completeness,
label and dependency checks. Honor explicit changes to review/encoding requirements.
Freeze exact quotas, deterministically replenish failures in the same stratum, and
record future-only sampling revisions without rewriting completed episodes.

```bash
python /path/to/skill/scripts/project.py plan --root work/task
python /path/to/skill/scripts/project.py next --root work/task
```

The ledger records receipts; it does not run the project adapter or certify its claims.
`seal` closes the dataset ledger only, not training, upload or real-world evaluation.

## Run a measured, durable pipeline

Read [rendering-server.md](references/rendering-server.md) and
[dataset-validation.md](references/dataset-validation.md). Overlap bounded CPU motion/
scene preparation, GPU rendering, native export and previews. Train from a frozen local
snapshot while its network upload proceeds. Measure actual throughput and memory before
increasing per-GPU concurrency; count physical GPU UUIDs and honor shared reservations.

Use fast previews and the requested final engine mix. Eevee's interactive capability
does not remove scene loading, shader compilation or export cost. Reuse an episode's
loaded scene and render camera sequences continuously where verified. Bind Eevee and
Cycles devices through their actual backends; CUDA visibility alone may not select EGL.

Provide per-episode synchronized preview videos with companion JSON and a directory
index when requested, without another GPU render. Maintain a read-only monitor showing
family counts, active worker/frame progress, export, training, uploads, failures and
stage-specific ETAs. Detach durable finite controllers, confirm they advance independently
of the agent session, and preserve restart commands and immutable receipts.

Privacy redaction is opt-in. Read [privacy-release.md](references/privacy-release.md)
when requested or packaging a release. Keep credentials and unrequested source caches
out of outputs. Upload to the authorized destination/visibility, then verify the remote
commit and inventory. Preupload, commit and verification are distinct states.

## Train, adapt and prepare rollout

Read [training-deployment.md](references/training-deployment.md) whenever models or
rollout are requested, and [rollout-diagnostics.md](references/rollout-diagnostics.md)
for runtime checks. Establish the hardware unit contract before large training. Use the
local validated dataset and official policy/processor APIs with pinned versions; load
only deployment-available camera/state features. Save resumable checkpoints and the
resolved training recipe. Choose budgets from a real throughput/VRAM smoke.

Verify both saved processors, action/state order, units, gripper calibration, action
semantics, camera layout and control rate. Run actual loaded checkpoints across complete
representative sequences, including chunk boundaries and release. Unit adaptation may
preserve weights, but is not a task-success repair. A portable positive-affine helper
is supplied in `scripts/adapt_policy_units.py`; read its supported boundary first.

Deliver model weights, config, processors, unit assumptions, validation, dataset lineage,
runtime version and an actual-model-specific command. ACT temporal ensembling and SmolVLA
RTC are different interfaces. Benchmark latency on the deployment GPU; memory fitting
alone does not establish control cadence. Do not claim hardware execution unless observed.

Read [evaluation.md](references/evaluation.md) for splits and generalization claims.
Keep derivatives of a source/seed group together; same-source fit is diagnostic. Report
render/data/training/deployment completion separately, maintain recovery state and make
an atomic commit. For historical evidence and remaining limitations, consult
[case-lessons.md](references/case-lessons.md) and [validation.md](references/validation.md).
