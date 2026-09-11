# From a minimal request to deliverable policies

## Resolve inputs without making the user design the pipeline

Prefer a demonstration video/dataset episode plus multiview photos: retain recorded
state/action and timing where available, and fit scene geometry/appearance with the
additional views. Support missing components rather than turning this preferred input
set into a mandatory upload checklist. Visual evidence plus a task can start a fallback;
actuator-level outputs also need an identifiable robot/control interface. Search metadata, EXIF, CAD caches, installed
drivers and prior instructions. Use official documentation when local code is missing
or unclear. Source download should start with metadata and selected numeric rows, then
only required cameras/episodes. A reference dataset can diagnose units without copying
its videos or incorporating it into training.

Record an intake matrix:

| Contract | Record |
| --- | --- |
| Evidence | photos/video/recorded states; immutable source IDs; measured/fitted/inferred fields |
| Robot | CAD revision, joint order and axes, zero convention, limits, gripper mechanism, controller |
| Sensors | camera keys, mount roles, resolution/crop, calibration, timestamps, RGB convention |
| Task | identity cues, initial distribution, observable search, contact/release, terminal predicate |
| Delivery | accepted count, formats, previews, models, local/public/private destinations |
| Resources | machine, GPU allowance/free reserve, CPU/disk limits, existing jobs, budget |

A task may specify some of these in ordinary language. Translate it into configuration;
ask only for unresolved decisions that change scope or make an output uninterpretable.
A photo-only source needs estimated dimensions, not a request for nonexistent joint logs.
Use robot dimensions for scale; record uncertainty and, when feasible, vary plausible
parameters. Do not hide incompatible calibration behind wider randomization.

“Just give me data” ends at the dataset. “Give me models I can rollout” includes training,
processor adaptation, runtime compatibility and a handoff command. Model architecture,
compute allocation and public publication should follow user scope/context. A simple
request is not authorization for unlimited training, paid asset generation or physical
actuation. Prefer local reviewable artifacts until a remote destination is resolved.

## Stage graph and observable completion

| Stage | Completion evidence | Work that can overlap |
| --- | --- | --- |
| Intake/control contract | source hashes, robot/sensor schema, inference assumptions | dependency setup and asset inspection |
| Scene | packed editable scene, calibrated views, appearance/geometry residuals | native writer fixture and deployment interface probe |
| Task seeds | search, grasp/interaction, release and terminal checks with explicit validation scope | preview rendering and appearance design |
| Production | admitted episodes with complete data/lineage, exact quotas | preparation, rendering, export, preview |
| Frozen snapshot | official native read, numeric/temporal checks, actual subset distribution | dataset upload and training independently |
| Training | requested step budget, final checkpoint, resolved config and logs | other model and ongoing later data production |
| Deployment | actual strict reload, both processors, unit/temporal checks, runnable command | model upload after local validation |
| Remote release | fixed commit, file hash/size inventory, requested visibility | unrelated local tasks |
| Real evaluation | recorded real trials and task outcome | subsequent diagnosis |

Do not make training wait for a dataset upload when local validated data exists. An
interim snapshot must be immutable and contain whole admitted episodes; call it a subset
and report its actual distribution. Later full data gets a distinct identity. Never
train while the same directory is being appended/reindexed or replace processors with
statistics from a later dataset silently.

Prepare the next independent stage early. A short official-loader/model smoke can find
feature and unit mismatches before thousands of images exist. Full training starts only
from the intended snapshot and within the compute allowance, not from the tiny fixture.

## Project adapter boundaries

Keep these modules independently cacheable: source contract; numerical FK/IK and contact;
scene assets; task seed generation; layout retargeting; observation augmentation;
renderer; native exporter; training adapter; deployment adapter; scheduler/status.
Use typed records and tensor shape comments. A shared source file is not automatically
a dependency of every stage: hash actual motion dependencies, then observation/render
ones separately. Do not hash an entire monolithic appearance builder as a motion key.

Recommended records include `source_contract.json`, `runtime.json`, seed reports,
candidate manifests, dataset snapshot/release manifests, per-model training progress,
`deployment_units.json`, offline runtime report and upload receipts. File names are
illustrative. Persist commands, process identity/start time, versions, errors, counts
and next resumable operation; a PID alone can be stale or reused.

The portable `project.py` freezes one dataset plan and serializes admission. It is not
a parallel job scheduler. Its `next` exposes one unresolved candidate per deficient
stratum: multiple workers must not race to claim the same candidate. Implement leases
or a prepared finite schedule in the project coordinator, keep atomic admission, and
retain the helper's exact-count/evidence semantics. A production sampling revision must
be explicit and future-only; use a new plan/session when the portable helper's frozen
request changes. Do not disable frozen-hash checks to resume a changed plan.

## A useful handoff

Deliver the editable scene and rebuild command; dataset snapshot and preview index;
model directories or verified repositories; resolved unit/sensor/controller contract;
model-specific rollout command; monitor/restart commands if computation continues;
and limits tied to evidence. “Training finished” is not “uploaded”, and “offline runnable”
is not “real task succeeded”. Do not leave model delivery at weights alone.
