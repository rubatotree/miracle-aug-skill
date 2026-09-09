# Showcase provenance

These are real Blender renders of the final reconstructed tabletop scene and its
task-conditioned variations. They are documentation examples, not camera recordings,
generated illustrations, or a completed training-dataset release.

| Image | Contents | Rendering |
| --- | --- | --- |
| [Overview](overview.jpg) | Reconstructed scene, reverse view, glass, alternate toy, colored light and metal | Six native 640 × 480 Cycles tiles, 128-sample limit |
| [Task sequence](task-sequence.jpg) | Frames 0, 240 and 427 of the same calibrated demonstration | Cycles, 128-sample limit |
| [Renderer comparison](renderer-comparison.jpg) | Same scene, camera and frame 240 | Cycles 128-sample limit / Eevee 64 samples |

Blender 5.0.1 was used. Cycles used OptiX, adaptive sampling and denoising. Eevee used
screen-space ray tracing and shadows; its indirect light and reflection appearance
differs visibly. The assembled JPEGs preserve the rendered image pixels apart from
JPEG compression and add only caption strips. No retouching, source-photo compositing
or EXIF/location metadata was added. Native frame hashes, effective quality settings,
source-scene hash and distributed-image hashes are recorded in [release.json](release.json).

The source scene owner explicitly requested exterior anonymization for sharing.
Exterior photo/panorama textures were removed and replaced by an opaque generated
mosaic, including the relevant reflection/transmission paths and unused packed images.
This changes the exterior's appearance; it is an intentional privacy transform for
this example. **MiracleAug itself does not redact by default.**

The full 428-frame trajectories for these cases passed the project's geometric and
visibility checks. Only selected final-quality frames are shown. The large production
batch was still running when the gallery was prepared; no full upload or policy
generalization result is implied. Unobserved parts of the room remain inferred.

## Asset sources

The scene and adaptation were created in the MiracleAug project. Third-party sources
visible in these rendered examples include:

- SO-101 CAD from The Robot Studio's Standard Open SO-100/SO-101 project. The vendored
  CAD package contains the Apache-2.0 license. No CAD files are included in this gallery.
- [Bunny Soft Toy by Yin Wu](https://www.blendkit.com/asset-gallery-detail/eb21a8a0-d3b0-4615-becd-1a842bfac171/),
  distributed with a CC0 designation in the asset provider's retained source metadata.
  The project fits a miniature instance to the task's grasp and container geometry.
- The mug carries a reconstructed SIGGRAPH event graphic; this is an appearance detail
  of the observed object and does not imply affiliation or endorsement.

The skill's MIT license covers original code and documentation. It does not change
third-party asset or mark rights. The gallery contains rendered examples only; raw
source video, the original surroundings, scene files and account information are absent.
