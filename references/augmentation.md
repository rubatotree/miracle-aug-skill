# Coverage, intensity and exact accepted quotas

The objective is useful nuisance robustness around a task, not a large mosaic count.
Represent each request as exact counts by family, weak/strong intensity and renderer.
Use largest-remainder allocation for proportions so totals are exact, then freeze the
resolved request. Preserve explicit user counts even if a different prior default was
used. Separate accepted episode count from attempts, rendered frames and sample count.

Possible families and dependencies:

| Family | Weak/strong examples | Required consistency |
| --- | --- | --- |
| Static camera | Small baseline / reverse or high-low oblique view | Intrinsics/extrinsics, room envelope, task visibility and intended sensor deployment |
| Dynamic camera | Small drift / orbit or sweeping motion | Continuous camera path; wrist mounts follow FK |
| Static lighting | Small exposure/tint / saturated side light, hard directional shadows | Same phase motion; actual world/light values |
| Dynamic lighting | Slow subtle intensity / moving colored lights and changing shadow direction | Full time-dependent light labels |
| Material | Slight hue/roughness / strong color, metal, matte, glossy, glass | Preserve geometry, realistic scale and engine limitations |
| Environment | Subtle backdrop tint / distinctly colored room/background/clutter | Solid support, occlusion, no new-view holes, privacy |
| Object pose | Small supported shift / larger reachable placement and yaw | Replan motion and recheck contact/collisions/success |
| Object style | Subtle silhouette / different cup or manufactured toy design | Task affordance, dimensions, anchor and updated task text |
| Trajectory | Mild timing / larger feasible speed/path change | Limits, synchronized states/actions and object/camera motion |
| Combinations | Weak pair / strong cross-family combinations | All coupled constraints; explicit constituent labels |

Choose only families meaningful for the actual task and user's scope. Strong
augmentation is not unlimited randomization: fully hiding the task, moving a camera
through a wall or making the manipulated object too large to fit creates invalid
training examples for a success-labelled dataset.

For lighting, verify visible color differences and cast shadows on the workspace.
For materials, compare metal/glass/glossy/matte appearance in both renderers. Uniform
flat color with no changed surface response does not satisfy a material request.
Generate contact sheets at rest/contact/release and a short temporal strip. Record
actual parameters and visual coverage, not just names like `strong_4`.

Seed candidate generation independently from render noise. Use discrete assets plus
continuous nuisance parameters to avoid pixel-identical repetitions. Measure duplicate
or near-duplicate trajectories and observations; repeated paths are expected for
observation augmentation, repeated identity imagery should not masquerade as diversity.
Keep asset/style distribution, combinations and rejection causes in coverage reports.

The portable `project.py` helper freezes family/strength/engine strata, generates finite
candidate IDs, and records immutable evidence-bound receipts. It does not implement
domain sampling; write that in the project adapter and include its hash in the runtime
checkpoint. Rejected geometry consumes an attempt in its own stratum. Infrastructure
failure retries the same candidate and never counts as geometric rejection. Exhausted
pools stop with diagnostics rather than reducing requested success count or creating
unauthorized extra accepted episodes.

Before scaling to thousands, benchmark representative engine/material categories,
run a small diverse actual task batch, and inspect semantic and image quality. Passing
geometry and changing seeds does not prove useful augmentation. Keep source-episode
lineage intact for leakage-free downstream splits.

## Sample relationships, not only independent object jitter

Task motion/layout and observation appearance are separate sampling layers. Build a
small library of verified motion/layout seeds, then generate many material/light/camera
variants per seed. Cache IK results, joint/object/deformation arrays and the animated
base scene before observation changes. Avoid repeated IK, keyframe construction and
packing for each texture variant. Report unique motion/layout seeds as well as episodes;
the latter count does not measure independent task diversity.

For tabletop placement, movable-layout randomization should include task objects and
all permitted distractors, subject to support, non-overlap and reach. Sample target and
receptacle angle/radius independently enough to cover both left/right relations and
near/far distances; rigidly rotating the original pair cannot fill all such gaps.
Retarget search, approach and placement consistently. Use one canonical robot/table
coordinate convention plus numeric positions; screen-left in opposite cameras reverses.
Record signed relative displacement and distance rather than ambiguous labels alone.

Target orientation needs an independent local-face axis. Record its angle/dot product
toward the robot and actual yaw: “far” was corrected by the user to eyes facing the arm
in this case. Do not preserve a mistaken verbal label as geometric truth. Include oblique
orientations, not only a 180-degree toggle. If the user specifies proportions for future
data, enforce them on the remaining eligible episodes and report final global counts
separately. Do not overwrite completed scenes to make old data satisfy a new preference.

Random distractor removal can include an only-target-and-receptacle tier. Never remove
the manipulated object, destination, robot or necessary support. Drop child geometry
and associated shadows/reflections together; avoid orphan fragments. Removing a load-
bearing/contact object needs replanning. Otherwise an obstacle-free subset can inherit
an existing path and save computation. Additional distractors need collision/visibility
checks; they are not the same operation as removal.

## Mix independent nuisance axes with task identity intact

Set the main distribution around realistic deployment variation. Single-axis examples
establish that each mechanism changes the intended property; mixed examples should
carry most training mass when broad robustness is requested. Use separate random streams
for layout, orientation, material, light and camera so adding one axis does not silently
resample all prior choices. Freeze the actual sampled parameters in each candidate.

Camera error has its own range/mixture. Ordinary placement offsets should be visibly
nonzero and reflect actual installation tolerance. Rare opposite/overhead views belong
to a separately budgeted extreme component; strong colored light need not imply an
extreme camera. Keep wrist extrinsic perturbations mount-relative, not independent of
FK. For an external camera, moving its stand is required only if the intended model
includes that stand; a user may explicitly authorize hypothetical viewpoints without
rearranging background furniture. Do not expose the task through a wall or label an
unobservable target-dependent action as an observable success demonstration.

Apply appearance to objects and surroundings, not only the tabletop: continuous colors,
roughness, glaze, metal, clear/tinted/frosted glass, wood, textile and irregular texture
where meaningful. Use environmental and local lights with changes in position, area,
intensity, color, shadow and direction. Preserve instruction-defining cues: a black cat
with yellow eyes and a green branded mug cannot silently become unrecognizable objects
under a success instruction that still names those features. Identity-changing variants
require corresponding task text/labels. Extreme low visibility should be explicitly
separated if training a different behavior such as searching or abstaining.

Maintain coverage by family, constituent axes, strength, engine/quality, left/right,
distance, face orientation, distractor count and unique seed. Record actual histograms
and outliers. Quotas and factors are task-specific; the previous project's 1280 count,
64/1216 engine split, left-cup proportion and orientation weights are not defaults.
