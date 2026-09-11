# Rollout continuity, latency and task progress

Diagnose the model and command actually being used. New user feedback supersedes an
older failure description: a robot now reaching the cup should not still be described
as unable to grasp. Record checkpoint revision, policy type, runtime version, overrides,
unit mode, actual control FPS and synchronized observations/action/feedback. Do not
attribute the same outcome to both trained models without evidence.

## Use model-specific execution

ACT predicts a chunk; executing only a few steps and replacing it can introduce
repeated discontinuities. Compare actual sequential `select_action` behavior under the
saved runtime defaults, longer prefixes and supported temporal ensembling. Useful
metrics include per-joint maximum step, angular velocity/acceleration, significant
reversals, tracking error and errors at contact/release. Compare to source motion:
large source accelerations cannot be blamed solely on inference.

For the tested ACT version, this optional pair enabled temporal ensembling:

```bash
--policy.n_action_steps=1 --policy.temporal_ensemble_coeff=0.01
```

This is an ACT starting point for comparison, not a universal optimum. Verify its
meaning in the installed implementation: do not infer which predictions a coefficient
weights more heavily from its sign alone. The case's two source-sequence tests reduced
acceleration and chunk jumps, while some descent errors grew. Neither result establishes
closed-loop stability. Compare explicit aggregation to the actual runtime at the same
precision; a float32 reconstruction is not bitwise equivalent to float16 accumulation.

SmolVLA does not accept ACT's `temporal_ensemble_coeff`. If CLI help lists SmolVLA
parameters, inspect `config.type` and policy path rather than retrying the ACT flag.
For high-latency SmolVLA, use a supported asynchronous engine with RTC to join chunks:

```bash
--inference.type=rtc \
--inference.rtc.execution_horizon=10 \
--inference.rtc.max_guidance_weight=10.0
```

These flags are documented in [official RTC deployment](https://huggingface.co/docs/lerobot/rtc).
Check the target installation exposes them and enables the policy RTC processor;
older runtimes may contain policy RTC code without the newer rollout engine. Do not
silently upgrade a live environment. RTC overlap/guidance and the queue refill threshold
are distinct controls. Tune them using measured delay and reactivity, not a copied GPU name.

If implementing/testing RTC directly, `predict_action_chunk` consumes a previous prefix
in the model's normalized action space, before hardware-unit postprocessing. Keep queue
versions of normalized and executable actions distinct. The tested guidance needs a
local autograd calculation: wrapping the whole path in `torch.inference_mode()` breaks
it even though outer prediction ordinarily uses `no_grad`. AMP handling differs between
synchronous wrappers and RTC engines; benchmark the actual path. Do not extrapolate a
synchronous AMP benchmark to an asynchronous guided runtime.

## Fit the compute schedule to the controller

A 25 Hz actuator loop does not require 25 complete chunk inferences per second. A chunk
of H targets spans H/f seconds; if replanning begins with Q unconsumed targets, its
usable buffer is approximately Q/f seconds. Require measured high-percentile latency,
observation age, transfer/driver overhead and scheduling jitter to fit that budget, and
inspect how the implementation compensates for inference delay. Long queues reduce
stalls but can weaken responsiveness. First-chunk warmup and steady-state timings differ.

Benchmark the actual checkpoint on the deployment GPU using the true camera shapes,
state dimension, task-token length and inference mode. Record cold load, warm median/P95,
allocated/reserved GPU memory and total process memory. A synthetic image benchmark
measures resources only. A 4090 measurement cannot establish 4060 speed, laptop power
behavior or end-to-end robot cadence. Memory fitting does not prove smooth control.

For flow models, fewer denoising steps can reduce compute but can change task behavior;
compare after a baseline. Compilation can add startup time/memory and needs a supported
runtime. Avoid changing camera resolution/crop as a first latency fix: it can alter the
visual distribution and spatial cues. Camera FPS is not control FPS; explicitly set both.
Check stale HTTP frames, RGB/BGR ordering, camera swaps, buffering and timestamp skew.

## Distinguish common failures

| Symptom | First discriminating evidence | Interpretation to test |
| --- | --- | --- |
| Moves to a middle pose, stays there | state/action ranges before/after processors; config and saved stats | radians consumed as degrees, normalized range mismatch, gripper-unit error, stale processor |
| Severe repeated jitter | sequential command/feedback and chunk boundaries; actual FPS | replan jumps, source discontinuity, stale input, latency or tracking limits |
| Observes but does not approach | front/side target visibility and live predictions | domain mismatch, camera contract, source search memorization or feedback leaving training support |
| Reaches receptacle, holds forever | raw policy jaw target, action actually sent, jaw feedback | phase stall versus command clipping/tracking versus physical opening |
| Opens but object remains attached | measured jaw state and contact geometry | insufficient opening, nominal zero error, cloth/appendage entanglement |
| New version behaves unchanged | loaded revision plus both processor hashes | running old process/snapshot or incomplete atomic publication |

For release, inspect the full predicted horizon as well as the executed prefix. If
release is always a few steps beyond a freshly replanned short prefix, repeated replans
can keep deferring it. Repeating a frozen-observation chunk demonstrates that mechanism,
not the real robot's root cause. Once the user confirms temporal ensembling is enabled,
reassess that hypothesis: finite history cannot retain old close commands indefinitely
when new predictions consistently command opening.

At the stuck pose compare three signals: policy target, post-limit command sent and
measured jaw position. If target remains held, examine phase progression and actual
images/state. If target opens but sent command/feedback does not, inspect limits, driver
and load. If feedback opens but the object stays held, inspect physical opening/zero
and contact. Gripper [0,100] is neither millimeters nor degrees. Do not install a timed
forced release or send 100 merely to make a success video; any changed release strategy
must still satisfy the task and observed support condition.

Include approach-to-release diversity in future seed design: varied entry state, visible
receptacle support, adequate opening duration and retraction that leaves the object.
If proposing dwell, recovery or larger opening, label it as a new strategy requiring
appropriate checking rather than a previously established cause/fix.

Report whether evidence came from source-sequence replay, frozen-observation analysis,
closed-loop simulation, user hardware feedback or recorded real trials. Only the latter
closed-loop task checks support real success; low training loss and plausible intent do not.
