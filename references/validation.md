# Validation record and remaining scope

## September 2026 skill update

The updated package passed 20 behavioral tests on Python 3.11 with optional PyArrow,
PyTorch and safetensors installed. Tests use synthetic fixtures and cover:

- Exact engine/family quotas, deterministic plans, same-stratum replacement, bounded
  exhaustion, idempotent receipts and frozen request/evidence changes.
- Reconstruction-only scope, primary dataset-plus-photos intake, photo-only fallback,
  requested ACT/SmolVLA scope without launching jobs or authorizing hardware/publication.
- Variable sequence lengths and state/action dimensions, multiple cameras, recorded
  command versus synthesized next-position semantics, boundary/time/transform failures.
- LeRobot v2/v3 selected-episode extraction and shared-shard metadata offsets.
- Independent positive-affine maps for state `(B,3)` and action `(B,H,2)`, nonzero offsets,
  unchanged weights/unused image statistics/metadata, both runtime processor endpoints,
  extra stored-but-unused moments, unsupported modes/shapes/scales and double adaptation.
- Deterministic release packaging, relative links, exclusion of unapproved media and
  credentials, and optional rather than automatic privacy redaction.

An additional CPU-only integration used the existing ACT and SmolVLA case checkpoints
with official LeRobot 0.4.3 processors. Both original and newly adapted processor pairs
were actually loaded. Synthetic observations and normalized action chunks gave maximum
state-normalization difference 1.25e-7 and inverse-mapped action difference 2.39e-7 in
training units. Action shapes were `(1,100,6)` and `(1,50,6)` respectively; model weight
hashes stayed unchanged. No model forward, robot actuation or fresh task evaluation was
performed by that integration. The case's source/calibration/checkpoints are not required
by or included in this package.

That integration exposed a real compatibility gap in the first helper draft: an SDK
postprocessor stored observation-state moments without declaring state as an active
feature. The helper now separates saved moments from declared runtime endpoints; the
synthetic regression fixture includes that case. This is why testing only self-created
processor JSON is insufficient for deployment compatibility.

Skill frontmatter and package link/inventory checks pass. Release verification includes
running helpers/tests from a relocated package and verifying the installed inventory.
The package does not vendor this project's photos, robot assets, private diagnostic
dataset, calibration or model weights. The earlier three showcase images remain hash-
bound historical examples; their provenance is unchanged.

## What this does not establish

No independent agent has yet rebuilt a new robot/task using this revised package end
to end. These tests establish helper behavior and one SDK compatibility point, not a
universal reconstruction/planning system. Future SDK versions need their own processor
and command checks. CPU processor equivalence is not full-model numerical equivalence,
hardware calibration or control-loop timing.

The primary demonstration-plus-multiview workflow is preserved. The photo-only case
produced a complete published native dataset and two published subset policies; the
full-data models were still training at this update. User feedback supports ACT grasp
and transport, with release unresolved. No improved policy generalization or complete
real-task success rate is claimed. See [case-lessons.md](case-lessons.md).

For forward testing, use a new demonstration and views in an isolated project, then a
missing-information variant. Inspect actual reconstruction and model handoff artifacts,
not whether prose repeats this skill. If delegation is explicitly available/authorized,
an independent task agent can test it without receiving the expected solution. Do not
launch unbounded rendering, paid services, uploads or hardware actions just to validate
skill wording.
