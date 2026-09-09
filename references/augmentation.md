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
