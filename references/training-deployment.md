# Training and the hardware interface

Read this before choosing the native action schema or launching substantial training.
The tested integration used LeRobot 0.4.3; newer releases move modules and change CLI
flags. Inspect the installed package/config classes and record exact versions. Verify
current official APIs rather than copying a historical command blindly.

## Define the control contract early

Store separate contracts for raw evidence, simulator, training and deployment. For each
state/action coordinate record name/order, unit, sign, zero, range and absolute/delta/
velocity/torque semantics. Match the simulator's action hold, interpolation and delay to
the real driver. Record camera FPS and control FPS independently. Gripper state under
load can differ from its requested target; do not substitute achieved state for command
without explicitly selecting that supervision rule.

For the tested SO-101 driver, five body motors use degrees with `use_degrees=true` or
calibrated [-100,100] otherwise; the gripper remains [0,100] in both modes. These are
not six radian coordinates. Driver defaults vary by version: explicitly set the mode.
The physical gripper rotates one jaw and is not a generic parallel-jaw opening model.
See [official follower implementation](https://github.com/huggingface/lerobot/blob/main/src/lerobot/robots/so_follower/so_follower.py).

The [official SO-101 description](https://github.com/TheRobotStudio/SO-ARM100/blob/eecbe3e0a9ebb23e25ad7b2759b03884c6660903/Simulation/SO101/README.md)
distinguishes old/new joint zeros and states that the LeRobot gripper convention is not
encoded in the supplied URDF/MuJoCo files. CAD limits alone therefore do not establish
the hardware gripper mapping. Use that robot's actual calibration and pose correspondence.

For a same-direction encoder with range span `s` ticks and driver resolution `R` ticks
per turn, a known jaw anchor `(q_a radians, p_a percent)` gives:

```
p = p_a + (100 * R / (2*pi*s)) * (q - q_a)
```

Check the SDK's resolution convention; the tested mapping used R=4095, not a universal
4096 assumption. Firmware homing offsets may already be applied to returned positions;
do not subtract them twice. Range midpoint is not automatically the URDF jaw zero,
and demonstration min/max is not a mechanical calibration. Explicit nominal endpoint
alignment can make a usable provisional package when official conventions support it;
mark `mechanical_zero_measured=false` and preserve the residual assumption. Do not stall
all work for an optional precision measurement, or silently call a nominal alignment exact.
No example calibration or jaw coefficient from the previous owner is a default.

If available, inspect a known working dataset's numeric state/action ranges and encoder
quantization to detect unit/offset mismatch. This is diagnostic evidence, not permission
to mix its private samples into training or publication. State and command may have
different leader/follower calibration; examine them separately.

## Fit official policies to the local native data

Freeze a local validated snapshot. Use the official dataset reader with the actual
local root/cache so Hub publication does not trigger a second dataset download. Record
the local manifest hash now and associate the remote commit when upload completes.
Keep training outputs outside the dataset directory and avoid modifying a running
environment. Pin dependencies; record any local patches and test their changed behavior.

Create an explicit feature allowlist: only camera streams, proprioception and task text
available at rollout. Simulator object poses, contacts, phase indices, success labels,
source time and augmentation metadata are annotations, not policy inputs. Task text and
camera keys must match the deployment model config exactly. Exclude terminal invalid
actions through the official padding/loss convention; do not leak the next episode.

For ACT, use the official ACT configuration and backbone; for SmolVLA, fine-tune the
intended official pretrained checkpoint and preserve tokenizer/image processor files.
Inspect the exact saved checkpoint architecture before accepting CLI overrides.
Record at least optimizer/scheduler, batch and effective batch, steps, seed, precision,
chunk size, action horizon, image transforms, normalization and pretrained revision.
`n_action_steps` controls execution prefix in applicable synchronous wrappers; it is not
necessarily the training chunk length.

Choose settings from a short real-data load/forward/backward smoke on an admitted GPU:
VRAM peak, throughput, loader wait and checkpoint size. Set a finite authorized step
budget, save resumable optimizer/scheduler/RNG state and keep progress atomic. Resume
from a valid checkpoint only when dataset identity and training configuration match;
use a new run for a changed dataset. An exit code without the requested checkpoint and
step count is not successful training. Track each model independently; return its GPU
to the shared renderer only if the current reservation rules allow it.

Evaluate representative complete episodes and phases with the loaded policy and saved
processors. Report arm and gripper errors in named units, action-window errors, range
excursions, release behavior, discontinuity and phase-specific results. Same-source
held-out augmentations are useful fit diagnostics but not independent real generalization.
Do not choose a model solely from low aggregate loss dominated by long idle segments.

## Adapt a checkpoint without retraining, when mathematically valid

For a positive diagonal affine coordinate change `h = a*q + b`, MEAN_STD processors
can use `mean_h = a*mean_q + b`, `std_h = a*std_q`. Both state preprocessing and action
postprocessing must change together; adapt stored action statistics in preprocessing
when present too. Keep model weights unchanged and save to a new deployment directory.
Do not also convert outside the model, or rebuild its processors from old radian data.

`scripts/adapt_policy_units.py` implements this narrow transformation for arbitrary
state/action dimensions with explicit independent maps. It requires PyTorch and
safetensors, as already provided in a suitable training environment. Example mapping:

```json
{
  "evidence": "Example only: derive from this robot's actual driver and calibration",
  "alignment_kind": "nominal",
  "features": {
    "observation.state": {
      "names": ["joint_a", "jaw"],
      "source_units": ["rad", "rad"],
      "target_units": ["deg", "percent"],
      "scale": [57.29577951308232, 40.0],
      "offset": [0.0, 7.0]
    },
    "action": {
      "names": ["joint_a", "jaw"],
      "source_units": ["rad", "rad"],
      "target_units": ["deg", "percent"],
      "scale": [57.29577951308232, 40.0],
      "offset": [0.0, 7.0]
    }
  }
}
```

The two-axis jaw values above are a mathematical example, not a robot preset. Supply
all coordinates, including identity mappings for unchanged axes, in actual tensor order.

```bash
python /path/to/skill/scripts/adapt_policy_units.py \
  --checkpoint training/final/pretrained_model \
  --mapping configs/deployment_mapping.json --output deployment/policy
```

The helper refuses unsupported normalization, nonpositive scales, incompatible shapes,
missing processor endpoints and double adaptation. It preserves unrelated tensors and
safetensors metadata and reports unchanged weight hashes. The SDK may serialize unused
state moments in an action-only postprocessor: distinguish stored statistics from the
features actually declared by that processor, while keeping matching moments consistent. It does not verify physical
zero, joint ordering against hardware, action semantics or the model's real behavior.
Sign reversals, reordered axes, nonlinear jaw geometry, quantile normalization or
coupled kinematics need an explicit adapter and independent tests, not this helper.

Finite precision and normalization epsilon mean the normalized-value identity may be
approximate. Verify the actual official pre/post processors using nonzero offsets and
real tensor shapes `(B,D)` and `(B,H,D)`. Then strictly reload original/adapted models on
representative observations with matched randomness. Separate preprocessing error,
postprocessing affine error and network rounding sensitivity. BF16 can amplify tiny
input differences; do not disguise that as exact weight-output equivalence. State
numerical tolerances in physical units or encoder ticks with measured residuals.

## Package for an executable handoff

A deployable artifact contains weights; policy config; both processor configs and their
state files; tokenizer/vision dependencies or resolvable pinned references; explicit
unit/calibration assumptions; feature order; control FPS; dataset lineage; runtime and
validation report; and a model-specific rollout command. Training metrics remain in
training units unless deliberately converted and labelled. Preserve the original
checkpoint/revision for reproducibility when publishing an adapted one.

Validate a fresh actual load from the deployment directory before upload. Verify shapes,
finite outputs, requested device, supported overrides, unit maps and complete sequence
behavior offline. Make the command include actual camera names/URLs or clearly marked
user hardware fields, robot ID/port, degree mode and FPS. Do not start a connected
physical robot merely to test CLI parsing.

Use the authorized repository name/visibility; publish all mutually dependent processors
and configs in the same commit with weights. Reuse unchanged model blobs. Keep uploads
asynchronous and verify the fixed remote commit's hash/size inventory after completion.
A moving `main` reference is not a reproducible version: report the resolved revision,
and offer a pinned revision/local snapshot for comparisons. Do not promise hot reload
in an already running process or a refresh in offline cache mode.

Primary documentation: [ACT](https://huggingface.co/docs/lerobot/act),
[SmolVLA](https://huggingface.co/docs/lerobot/smolvla),
[native dataset format](https://huggingface.co/docs/lerobot/lerobot-dataset-v3).
For runtime cadence and release failures, continue to
[rollout-diagnostics.md](rollout-diagnostics.md).
