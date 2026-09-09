# Lessons from the implemented tabletop reconstruction

These are transfer lessons from one project, not a generic parameter preset.
The source was one six-channel SO-101 demonstration, 428 frames at 30 fps, with a
fixed task camera and a separate wrist stream. Supplemental phone orbit video helped
with appearance and geometry; it was not another task trajectory. The pipeline
reconstructed the fixed/novel camera stream and explicitly omitted the wrist channel.

Metric CAD and a separated link hierarchy were essential. Robot calibration and
source-video timing were fitted using multiple phases. A tabletop/jaw intersection
could look acceptable in a low-resolution overlay, so full geometric clearance checks
were needed. Toy attachment had to preserve jaw contact and fit inside a real mug
cavity at release; parenting alone did not establish success.

The user rejected two procedural alternate-toy designs as implausible. Complete
licensed toy models, cleaned and fitted as coherent objects with metric grasp anchors,
produced more convincing results. Their existing topology and pose still needed
contact/cavity validation; an attractive downloaded model is not automatically valid.

Novel cameras exposed incomplete room/exterior geometry and problems with photo-card
coverage. Continuous plausible surroundings and explicit uncertainty labels were
necessary. Supplemental views supported some surfaces; unseen extent remained inferred.
Later privacy requirements replaced all original exterior imagery in a separate branch,
including packed unused images, instead of weakening the original calibration baseline.

A shared flash near eight seconds appeared in all mosaic cells. Source PNGs remained
stable while the decoded video changed at a keyframe. A revised master encoding
removed that measured jump. Window weave also needed physical-scale detail and temporal
inspection; the encoding diagnosis did not make every possible aliasing issue disappear.

The native export carried degree/normalized state, calibrated radians, synthesized
next-position targets with terminal validity, original commands separately, camera and
object matrices, task identity and source lineage. An official SDK roundtrip used a
tiny fixture to check pixels and temporal action padding before long rendering.

Mixed Cycles/Eevee rendering required actual quality labels and distinct device
selection. On the tested headless multi-GPU server, OpenGL initially fell back to the
first GPU despite CUDA visibility. An EGL device adapter matched NVIDIA devices by PCI
address and was checked using actual rendering processes. This workaround requires
revalidation on other systems.

At skill extraction, a new finite batch of 64 Cycles and 1216 Eevee episodes had been
launched after sparse privacy/engine smoke tests. Full batch completion/upload was
still asynchronous. No trained-policy generalization result had been established.
Do not turn launch status into a claim that thousands of validated episodes or a
robust policy already existed. Local artifacts and credentials are not required by
this generic skill and are not distributed with it.
