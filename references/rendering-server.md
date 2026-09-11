# Rendering, scaling and unattended execution

Keep the editable source checkpoint separate from a frozen production scene/config.
Select Blender and dataset SDK versions deliberately and record exact builds, GPU
driver, devices, resolved dependencies and source/code/asset hashes. Prefer isolated
environments. Verify downloads against official checksums. Do not overwrite another
project's environment or kill other users' GPU jobs.

## Engine profiles and device proof

Store actual engine, sample count, adaptive settings, denoising, ray tracing/GI,
resolution, exposure, view transform and weight. Do not trust a profile name as proof
of the scene's effective settings. Preview overrides need their own labels. Use a
bounded engine enum with explicit metadata codes and code-to-name mapping.

Cycles CUDA/OptiX device visibility and Eevee OpenGL/Vulkan device selection are
different mechanisms. `CUDA_VISIBLE_DEVICES` alone did not bind Eevee on the tested
Linux multi-GPU server. Prove each worker's device via actual render PID + GPU telemetry
on at least two distinct GPUs. A successful renderer string that just says RTX 4090
does not distinguish eight identical GPUs.

For headless NVIDIA EGL on Linux/glibc, [egl_device_affinity.c](../scripts/egl_device_affinity.c)
is an optional process-local adapter tested with Blender 5.0.1. Build it locally on
the server and scope it only to the Blender subprocess:

```bash
gcc -shared -fPIC -O2 -Wall -Wextra scripts/egl_device_affinity.c -o libegl_affinity.so -ldl
env -u CUDA_VISIBLE_DEVICES ASTRA_EGL_PCI_BUS_ID=0000:48:00.0 LD_PRELOAD="$PWD/libegl_affinity.so" blender -b scene.blend --python render.py
```

Replace the illustrative PCI ID using the server's `nvidia-smi` inventory. The shim
matches EGL's NVIDIA CUDA ordinal to a PCI address with an unmasked CUDA inventory,
and fails when no match exists. It is not a portable Blender API. Driver/OS/backend
changes require a fresh probe; Mesa enumeration and DRM permission failures can cause
fallback to a different GPU. Do not apply it to Windows, macOS or Vulkan. Use supported
backend controls when available, or a verified isolated worker/device environment.
EGL ABI references: [Khronos registry](https://github.com/KhronosGroup/EGL-Registry)
and [Blender's EGL context](https://github.com/blender/blender/blob/v5.0.1/intern/ghost/intern/GHOST_ContextEGL.cc).

Use Cycles for the requested higher fidelity subset and Eevee for standard data.
Check glass, glossy reflections, colored shadows and indirect light in both. Share
geometry, camera, time and label generation, but acknowledge engine-specific appearance.
Configure weights separately from quality tiers; equal weight one is a neutral starting
point, not evidence of the best training recipe.

## Benchmark and video QA

Render sparse actual task frames at final quality for each representative expensive
profile, including transparent materials. Measure startup/shader compile, scene load,
validation, per-frame rendering and encoding separately. Use cold and warm timings.
Estimate batch time from category-weighted timings, available worker count and measured
utilization, then add export/preview/upload costs. Report a range and assumptions,
not a linear extrapolation from one unusually easy frame.

Render cell videos at the requested native size and frame rate. Keep mosaic outputs
separate from training camera videos; pad incomplete final pages to the promised grid
dimensions and generate requested half/quarter sizes. Include cell-index/renderer maps.
Verify PTS, count, dimensions and alignment to labels using export receipts and the
agreed decode sampling scope. Decode suspect clips when diagnosing observed defects;
do not repeat all-frame compression QA by default.

To diagnose flicker, compare source PNGs and decoded video around the problematic
time, including keyframes. In the implemented case a shared flash at a GOP boundary
was an encoding artifact despite stable PNGs. An H.264 CRF 0 master after YUV conversion
removed that artifact; this is not lossless RGB because chroma conversion/subsampling
still changes pixels. Record codec/pixel format/GOP. Temporal denoising, undersampled
weave, coplanar surfaces, transparency sorting and changing random seeds need separate
investigation. Do not “fix geometry” without evidence it caused the defect.

## Durable finite jobs

Use one coordinator, process/session locks, measured bounded worker concurrency per
admitted GPU, bounded infrastructure retries and atomic progress files. Save candidate/scene checks, full
annotations, per-frame checksums and manifests so resume reuses verified work. Never
reuse cached frames after scene, labels, engine settings or calibration changed.
Checkpoint each completed candidate rather than waiting for a thousand-job batch.

Before launch, estimate peak disk using measured PNG/video sizes, temporary files,
export copies and three mosaic scales. Avoid duplicating large review trees. Monitor
free disk and stop with preserved progress before exhaustion. Do not delete source
data; any cleanup is limited to verified regenerable outputs within the session.

Run the supervisor in tmux, a user service or an equivalent detached process. Confirm
it is alive and advancing after closing the launch connection. Preserve logs, frozen
hashes, status and restart commands. Completing the selected count must stop generation;
no automatic expansion. Failures should leave resumable state and a clear diagnosis.

Verify the server can reach storage/Hub independently of local SSH forwarding. If the
user authorized a server proxy, store its configuration/credentials privately and
scope it to the job. Do not log proxy URLs with passwords or copy them into releases.
Render/export can run while upload waits for connectivity, but distinguish upload
preparation from a completed remote commit. Use bounded retry/backoff and resumable
large-folder transport where supported by the pinned Hub client. See the
[official upload guide](https://huggingface.co/docs/huggingface_hub/guides/upload).

## Throughput comes from overlap and reuse

Start with one process per GPU rendering a complete episode after one scene load.
Benchmark a second independent episode on an already admitted GPU if utilization is
low, memory allows and CPU/I/O is not saturated. Compare completed frames/episodes per
wall time, not the displayed utilization percentage. Eevee may benefit from concurrent
workers; Cycles may be better exclusive. These are measured scheduling choices, not
universal per-card limits. Include both warm/cold periods and expensive material classes.

Use continuous per-camera animation rendering when it preserves camera switching,
per-frame annotations and required settings. Repeated `write_still` can rebuild expensive
contexts. In the case, continuous Cycles rendering reduced 24-frame probe time by about
1.76x; dual Eevee processes increased sampled throughput about 1.94x. These local probes
are not promised speedups elsewhere. Native curves also reduced scene overhead. Lower
Eevee samples for permitted long-tail tiers and record the actual values; geometry,
shader load, readback and encoding remain costs even when rasterization is fast.

Pipeline bounded CPU layout/IK/base-scene preparation ahead of GPU work, then overlap
native export and preview encoding. Control prefetch using memory/disk and measured
rates. Share verified motion seeds across appearances. Vectorized labels and safe reuse
of already generated PNGs can avoid redundant compression. Same-filesystem hardlinks
are useful only for immutable data; do not mutate a linked file later. Keep original
sources and ensure cleanup cannot delete the last recoverable output.

Schedule by physical GPU UUID and ownership across rendering, training and probes. A
multiworker GPU is still one card. Apply the user's cap and reserve against current
external workloads; never kill those jobs. When training is authorized during rendering,
drain chosen render slots, reserve the cards, then start training. On completion release
only the finished model's reservation. Prevent starvation: do not refill every Eevee
slot forever if queued exclusive Cycles work needs a drained card. Do not serialize two
independent models behind a network upload.

## Resume without throwing away completed work

Freeze candidate parameters and record code/asset/runtime identity at worker launch,
not only after completion. A live source edit must not be presented as the old process's
executed code. Separate motion, appearance and renderer dependency keys. Changing a
logo or distractor visibility should not cause every valid IK cache to fail, but must
invalidate stale rendered appearance. Cache migration needs a recorded equivalence
argument and a bounded version transition; never treat any changed hash as compatible.

Adopt running workers at an explicit coordinator boundary when supported. Existing GPU
children can finish while CPU code switches; retain their original manifests. A new
parent may not obtain `waitpid` exit status: report a receipt-derived completion as such,
then check the receipt/output, rather than fabricating an observed process exit code.
Use finite infrastructure retries of the same candidate and semantic replacement within
the same stratum. Exhaustion is a resumable error with evidence, not an endless loop.

## Monitor the actual pipeline

A read-only watch tool should show:

- Total admitted/target, prepared/rendered/exported/preview counts and per-family quotas;
  real motion/layout/orientation/quality coverage when requested.
- Each worker's candidate, engine, physical device, actual completed/expected frames,
  throughput, elapsed time and live process/start identity; CPU queue and export backlog.
- Each model's steps/target, recent steps per second, loss, checkpoint and estimated time.
- Upload hashing/preupload/commit/remote-verification progress, bytes/files, retry/error,
  resolved repository/commit and durable completion notification.

Use atomic JSON receipts and actual files/process telemetry, not old status strings
alone. The monitor must not take upload cache locks, call SDK accessors that mutate or
clear metadata, restart jobs or trigger downloads. Read the pinned uploader's format
carefully. If only completed-file bytes are available, label them; do not invent live
intra-file network counters. Prefer authoritative final remote receipts over cached
partial totals. Upload retries should resume without retransferring completed files.

Estimate stage ETAs using recent measured rates and remaining work by engine/class.
The finish time of concurrent training and upload is their critical path, not a sum;
include queued work and shared CPU/disk contention. Show uncertainty or unavailable
until enough measurements exist. A render ETA does not include unknown training time.
Publish milestone notifications in persistent state so they remain visible after the
agent disconnects. Verify detached supervisors, child processes, logs and independent
network access before telling a user they may close the session; the machine still
must stay running.
