# Two cases, distinct evidence

The main use remains a measured demonstration plus multiview photos. The second case
shows a fallback when no demonstration is available; it does not replace that preferred
input. Do not mix the two cases' cameras, counts, calibration, privacy or validation.
All dimensions, rates, phase lengths and proportions below describe cases, not presets.

## Earlier demonstration reconstruction: historical gallery

The distributed showcase images came from a 428-frame, 30 Hz SO-101 demonstration with
six state channels, a fixed task camera and a separate wrist stream. The reconstructed
training stream in that project explicitly omitted the wrist channel; that omission is
not appropriate by default for new users. Supplemental phone orbit imagery constrained
appearance and room geometry. The exterior was replaced at that scene owner's request;
privacy redaction remains opt-in.

Metric separated links, source timing, container cavity and release checks were important.
Low-resolution overlays missed jaw/table penetration. Licensed complete alternate toys
outperformed two poor procedural proposals in that case, but source-directed manual
modeling worked better in the later case. New views exposed background card coverage
and parallax problems. A common mosaic flash was traced to encoded frames while source
PNGs stayed stable; this does not justify repeated compression QA in every later project.

The original skill recorded a launched 64 Cycles / 1216 Eevee batch, not a completed
release or demonstrated policy generalization. Its gallery/provenance remains historical;
no later completion from another source should be attributed to those pictures.

## Photo-driven black-cat task: September 2026

Input was ten multiview photos, an identified SO-101 and a text task, with no measured
joint logs or task demonstration. The user asked for autonomous reconstruction and
synthetic demonstrations, eventually training ACT and SmolVLA. Camera outputs were
front (wrist) and side (external), 640×480 at 25 Hz. Motion, flexible material properties
and much of the scene calibration were inferred. Official CAD and task-specific expert
planning were used. “Zero recorded demonstrations” is accurate; “no priors or tuning” is not.

The complete native dataset contains 1280 episodes and 384000 frames: 64 Cycles and
1216 Eevee with actual quality tiers. The public dataset release was verified at commit
`1763c06683fc94f63d7d53863197b4fdaac99b10` in
[rubatotree/miracle-pick-black-cat](https://huggingface.co/datasets/rubatotree/miracle-pick-black-cat).
Each episode has a synchronized inspection video and JSON. An earlier immutable 256
subset supported completed, published ACT and SmolVLA training. At this skill update,
the full-data training jobs were still running; they are not reported as completed here.

### Reconstruction lessons

The initial scene looked plastic. Real-scale cloth/floor texture, plush fibers and
correct grazing response mattered more than uniform roughness. Geometry and source-
image details needed separate evaluation. The white toy was a chef seal; semantic
correction changed the geometry. Direct sewn-panel modeling better preserved the target
cat's long body and embroidery than a generated proposal. Generated assets were useful
references, not automatically accepted models.

The SIGGRAPH mug print had to match side-view wrapping as well as the logo itself.
Multiple builders/cached scenes restored rejected artwork until a shared approved asset
was used. Dense legacy curves cost time; equivalent native curves improved speed but
Eevee appearance still needed checking. A source-view geometry fit or image hash change
was never sufficient evidence that the whole scene looked real.

### Motion and success lessons

The expert first used a target-independent observation motion, then validated visibility
before approaching. Simple eye/cup color checks had distractor/reflection false positives.
Only actual deployed front/side inputs were used for policy training; simulator poses
remained privileged expert/annotation data.

The user permitted strong plush grip, slight vibration and stable rim-spanning placement.
This widened the valid outcome, but did not remove the need to release and retract.
Outer commands, internal servo targets and achieved state were distinct. Substep velocity
spikes were hidden by 25 Hz sampling. A soft-contact force implementation issue required
an isolated corrected solver and revalidation; lower penetration and visually smooth
shells alone had not established sound physics.

A half-turn wrist branch addressed the front camera cable preference. Later manual
hardware feedback confirmed ample slack, allowing a wider practical motion envelope.
This was a case-specific physical constraint, not a reason to force all robot wrists
into the same orientation.

### Distribution and production lessons

Verified motion/layout libraries supported many observation variants. Full-table layout,
left-container/right-target and farther spacing needed intentional coverage. Target face
orientation and oblique yaw needed independent sampling. Distractor removal, including
only cat and mug, added simpler scenes without a new path when removed items were not
supports. The user's intended meaning of a direction label was corrected explicitly.

Most data used mixed perturbations; material changes included objects/backgrounds and
near lights. Ordinary camera-placement errors and rare reverse/extreme views were
separate factors. Weak ranges changed during production; later specs preserved the new
numbers without relabelling already rendered episodes. A later gallery review found
two side-occluded samples and excluded them from that gallery only. This is a known
coverage/inspection limitation, not evidence those dataset episodes were repaired.

CPU preparation, per-episode GPU rendering, native export, preview and upload overlapped.
Motion caches stopped invalidating on unrelated appearance edits. One probe measured
about 1.76x faster Cycles context reuse; another about 1.94x sampled Eevee throughput
with two workers on a card. Neither is a universal speed guarantee. The scheduler tracked
physical GPU UUIDs, left the requested free card, avoided external jobs and prevented
Cycles starvation. Upload and local training ran independently from the same frozen data.

Native export/merge found uint8 statistics overflow and missing annotation label maps.
Small official-reader fixtures and vectorized checks found these without repeated full
rendering. The monitor distinguished accepted/rendered/preview counts, live workers,
training, uploaded files and verified remote commits. Disabling redundant compression
checks did not mean ignoring missing frames or wrong action indices.

### Deployment and the unresolved boundary

The first published training interface used six radians; the SO-101 driver expected
body angles or normalized ranges plus gripper percent. Models moved toward a middle
pose and stopped. Both saved processors were converted with a positive affine mapping,
weights unchanged, using explicit driver degree mode and control FPS. The gripper used
a nominal model-to-hardware closed alignment and actual encoder span; physical jaw zero
was not measured. A private known-good numeric dataset was diagnostic only and is absent
from the skill and public artifacts.

Two complete source-sequence ACT analyses found that temporal ensembling reduced large
chunk transitions substantially, with some phase errors increasing. The user later
reported ACT with ensembling could grasp and transport the cat above the mug, but would
not release. That is partial real behavior, not a successful complete task. Release
exists in source labels and offline predictions; current live target, sent command and
jaw feedback are needed to separate a policy phase stall, tracking limits and inadequate
physical opening. A short-prefix counterfactual did not establish the cause once actual
ACT ensembling was confirmed.

A separate SmolVLA resource probe on RTX4090 measured about 1.18–1.22 GiB peak PyTorch
allocated memory for two cameras and a 50-action chunk. Ten-step median chunk times were
about 347 ms synchronous AMP and 412 ms with direct RTC guidance; five-step versions
were about 207/239 ms. Inputs were synthetic uniform images, no camera/robot I/O, and
this was not a 4060 or full asynchronous rollout test. It supports measuring buffer/
latency explicitly, not promising hardware task performance.

Transfer the mechanisms and evidence boundaries above. Do not reuse this owner's
calibration, fixed task phase times, engine proportions, seeds, GPU IDs or partial
hardware outcome as another project's validated recipe.
