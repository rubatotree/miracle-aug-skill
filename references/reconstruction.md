# Editable reconstruction and evidence gates

Use a project structure such as `source/`, `assets/`, `blender/`, `adapters/`,
`configs/`, `checks/`, `renders/`, `dataset/`, with a roadmap and development log.
Keep source observations immutable. Scripts should rebuild or deterministically amend
a saved checkpoint; Blender Text blocks are not the only copy of implementation.

## Metric structure and calibration

Import official CAD/URDF where available. Preserve each link's visual transform and
joint origin/RPY separately from its animated DOF. Validate zero pose, link lengths,
joint axes, handedness and FK against an independent numerical implementation. Convert
degrees/normalized gripper signals through an explicit calibrated mapping. Preserve
recorded states even if fitted joint offsets are needed for rendering.

Fit camera and layout from stable landmarks distributed in depth and across the image:
table edges/contact plane, robot base and joints, rigid prop silhouettes and handles.
Use metric robot dimensions to break scale ambiguity; state remaining camera/scale
degeneracies. Estimate a small parameter set before introducing detailed geometry.
Use robust reprojection loss, silhouettes/contact constraints and priors on plausible
calibration. Do not optimize lighting to hide displaced geometry.

Keep the camera and robot coordinate convention explicit. For pixel projection use
`p_camera = inverse(world_from_camera) @ p_world` followed by `K`; export OpenCV
right/down/forward separately from Blender's local camera axes. Check projected corners
with rendered markers. Intrinsics must reflect cropping, scaling and content rectangles.

Fit timing using multiple moving landmarks and contact events. Prefer a justified
small time map over arbitrary per-frame corrections. Store `source_state_time(t)` and
`source_video_time(t)` separately; interpolation must respect joint wrap and gripper
semantics. Do not edit raw logs to conceal residuals.

## Solids and unseen views

Task objects require actual volume: table thickness, container cavity and rim, handle
wall connections, jaw clearance, plausible undersides. Give each object a meaningful
origin and named material. Verify normals, disconnected fragments, manifold contact
surfaces and object hierarchy. A fused textured scene, image cards passing the source
overlay, or a skinned toy glued into the robot is not an editable reconstruction.

Use multiview evidence to constrain dimensions/materials and fill the scene around
the task. Review reverse views, low/table-edge views and extrema of allowed camera
motion. One exterior photo plane can expose empty space, clamped texels or wrong
parallax under new cameras. Build a continuous plausible background/room volume or
constrain the camera envelope; annotate which geometry is inferred. Distant environment
proxies may be acceptable if they pass the requested view envelope and privacy rules.

For alternate toys, use a coherent modeled or licensed asset rather than ornamenting
an ill-shaped blob. Inspect rest/grasp/release closeups. Scale a whole coherent design, preserve its
recognizable face and appendages, clean topology and align a metric grasp anchor.
Check license/attribution at the asset source. Paid generation is optional and subject
to existing spending authorization, never required merely because a service exists.

## Appearance after geometry

Fit exposure/color management and dominant light direction against the main demo.
Use physically interpretable surfaces: printed polymer, ceramic glaze, metal,
transparent glass, fabric, painted wall and laminate. Reuse shared material families
for matching parts. Avoid baking phone-video highlights into albedo. Separate decal
alpha from substrate response; prevent duplicate glossy layers and coplanar surfaces.
Add detail at metric scale and the requested pixel footprint; bevels, roughness,
micro-normal and fabric weave should survive downsampling without temporal aliasing.

Compare reference and render under matched dimensions/timestamps/color transforms.
Save overlay, difference and edge/silhouette views; use task-region masks so a large
bright window does not dominate an average image error. Report residuals per landmark,
robot/object ROI and phase, plus human visual findings. Thresholds depend on image
resolution, task clearance and source uncertainty; record the choice before declaring
a pass. Do not use a universal MAE threshold as the only gate.

## Intermediate checkpoint

Save `scene.blend`, regeneration scripts and `scene_checkpoint.json` only after:

1. Source-view geometry overlays pass at rest and multiple moving phases.
2. Separate CAD/solid assets and correct hierarchy are present.
3. Full motion passes contact, containment, continuity and collision checks.
4. Observed multiview geometry is consistent; inferred areas are labelled and have
   plausible appearance throughout the allowed new-view envelope.
5. Material/light consistency and sparse final-quality renders have been inspected.

List evidence files and hashes, residual metrics and limitations. A failed property
must remain failed. For scene-only scope, deliver here. For authorized augmentation,
continue from this immutable checkpoint. Never call an unseen region measured truth.

## Photo-only reconstruction and appearance corrections

Use metric robot parts and multiview table/rigid-object constraints to estimate scale.
Phone focal length equivalents, source crop and output aspect ratio are different;
resolve intrinsics for the actual content rectangle without stretching the photograph.
Fit shared rigid landmarks before flexible plush surfaces. A low residual on cup rims
alone does not certify the entire scene or a second camera. A view supplied later may
show a different object pose; do not force inconsistent captures into one rigid fit.

Create a semantic inventory before detailing: identity, silhouette, orientation, material,
markings and evidence views. The second case's white object was a chef seal, not an
unspecified white blob. User corrections update that inventory and the builder. Complete
coherent geometry can come from direct modeling, procedural construction or a licensed
asset; choose from source fidelity, editability and time. An earlier project's preference
for downloaded toys is not a reason to override a user requesting direct reconstruction.
Paid/image-to-3D proposals need lineage and rejection tracking; reuse completed downloads
and never resubmit merely because the agent forgot the prior result.

When a scene looks plastic, separate geometry, albedo, roughness, normals/fiber structure,
lighting and camera response. Compare one factor at a time under fixed views/light.
Large tabletop, floor, walls, bedding and large toys dominate perceived realism: give
them plausible nonuniformity at physical scale, not only flat Principled colors. For
fabric include seams, stitch placement, directional/grazing response and surface fibers
where their pixel footprint matters. Put fine detail into appropriate geometry/normal/
roughness channels; avoid regular sine folds or uniform hair lengths that reveal CG.

Reference-derived textures should use clean patches, perspective rectification and
illumination removal where possible. Record that recovered albedo/roughness is inferred,
not a measured BRDF. Preserve macro color and face cues. Black cloth washed gray by
specular response should not be repaired only by darkening the entire room. Different
brightness on horizontal and vertical fabric can come from grazing sheen; compare a
material hypothesis before an endless sequence of light changes.

For a cylindrical printed mug, verify artwork shape, alpha, scale, vertical placement,
wrap angle and relation to the handle in the main failing view and other supplied views.
A correct logo file can still be placed incorrectly. Use an authoritative logo source
when needed, record its origin, then fit the actual product print; a current event logo
may differ from the mug's printed year. Keep it a surface print, not thick embossed wire.
After acceptance, use one shared asset ID/hash and application function across canonical
scene, cached seeds and production. Validate that asset selection, so an old cached
blend cannot silently restore the rejected decal.

Keep collision, deformation and render meshes separate but mapped. New target geometry
invalidates its old contact volume and grasp checks. Do not extend that invalidation to
unrelated physics merely because a background texture changed. For dense fur, measure
native Blender curves versus legacy bevel objects; preserve coordinates, radii, masks,
material and deformation while changing representation. Test both final engines: a
faster representation may still create Eevee sparkle or disappear through refraction.
