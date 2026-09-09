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

For alternate toys, prefer a complete licensed toy model over ornamenting an ill-shaped
blob. Inspect rest/grasp/release closeups. Scale a whole coherent design, preserve its
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
