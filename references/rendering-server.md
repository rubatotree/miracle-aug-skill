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
Decode every finished clip, verify PTS, count, dimensions and alignment to labels.

To diagnose flicker, compare source PNGs and decoded video around the problematic
time, including keyframes. In the implemented case a shared flash at a GOP boundary
was an encoding artifact despite stable PNGs. An H.264 CRF 0 master after YUV conversion
removed that artifact; this is not lossless RGB because chroma conversion/subsampling
still changes pixels. Record codec/pixel format/GOP. Temporal denoising, undersampled
weave, coplanar surfaces, transparency sorting and changing random seeds need separate
investigation. Do not “fix geometry” without evidence it caused the defect.

## Durable finite jobs

Use one coordinator, process/session locks, one worker per admitted GPU, bounded
infrastructure retries and atomic progress files. Save candidate/scene checks, full
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
