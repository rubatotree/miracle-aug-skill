# Task-conditioned motion, not just changed pixels

Define the task oracle before augmentation. For pick/place it includes stable rest,
jaw contact, object following the gripper, placement within a real cavity or on an explicitly permitted support such as a rim,
release, and stability after retraction. For pushing it includes support/contact and target
region; for a drawer it includes articulation limits and handle engagement. Describe
the relevant geometry and phases rather than assuming all tasks grasp a plush.

Use the robot's actual DOFs, limits and controller representation. Create independent
contact geometry if visual fur/detail is too expensive, and record approximation/error
bounds. At contact transitions preserve world transforms; interpolate constrained
attachment only when the observed physical event supports it. A smooth blend that
slides through a jaw or wall is still invalid. Keep rigid objects separate from the
robot; soft deformation is object-local and cannot excuse impossible penetration.

For a new contact/motion seed, validate its full trajectory, with extra temporal
subdivision near fast movement or small clearances. For derivatives, use the dependency
and validation tiers below rather than rerunning the seed physics. Check FK, limits, finite velocities/accelerations, support penetration,
non-contact collisions, camera collision/clearance, grasp anchor consistency and task
success. Sparse images are for visual review, not a substitute for full trajectory
checks. BVH/convex tests and signed distances must use evaluated world geometry,
including modifiers, object scale, articulation and shape keys.

Changing lighting/material/background generally permits the same calibrated motion.
Changing a mug pose, toy dimensions, handle or target height may require constrained
IK/replanning. Keep unaffected phases, solve the changed phase using a warm-started
bounded optimizer and continuity/smoothness penalties, then validate the entire path.
Do not make an underactuated arm achieve an impossible full six-axis target. Retry
within the same augmentation stratum when clearance or joint limits fail.

A temporal warp is shared by camera, robot, object, light, deformation and annotations.
Monotonicity alone is insufficient: transformed velocity/acceleration can violate
limits. A dynamic external camera may be a useful observation augmentation; a wrist
camera must remain attached to the robot with a physically realizable mounting
transform. Label independent novel cameras separately; do not copy source wrist
footage while changing the scene and claim it is synchronized reconstructed imagery.

Preserve recorded actions as `source.action`. If producing next-position control
targets, explicitly define `action[t] = rendered_state[t+1]`, units and controller
mapping, with a held final target marked invalid. This equation is a synthesis policy,
not a universal property of robot datasets. Torque, velocity, delta-pose and chunked
policies need their own mappings. Observation changes do not justify changing command
semantics. Distinguish kinematic demonstrations from force/dynamics ground truth.

## Observability and physical operation

Use only the cameras that will exist during deployment. In the photo-driven case,
`front` was wrist-mounted and `side` external; neither a bird's-eye reference nor simulator
object coordinates was an extra live sensor. Define the causal sequence: independent
workspace search, current-frame target/receptacle acquisition, approach, contact, transport,
release and retraction. Search waypoints must not be selected from a hidden target pose
while described as visual discovery. Fresh frame evidence, timestamp and useful target
pixel area matter; mere projection inside a frustum does not prove recognition.

A semantic image test should include a missing-target negative control and likely
confusers. In the case, a colored distractor resembled eyes and green reflection on fur
resembled the cup. If an RGB heuristic is only a seed-validation aid, say so; the learned
policy is not automatically running that detector. Keep privileged expert planning
separate from deployment inputs. Recheck representative search views after changed target
layouts/orientations; an old visibility pass may no longer apply.

Model the actual wrist camera housing/mount and task-relevant cable constraints. Allow
an alternative wrist-roll branch (including a half turn when feasible) to reduce cable
twist, preserve a hanging cable's slack and avoid sweeping it across the workspace.
Do not assume a cable's shape or restrict all future poses from one imagined collision.
Use measured/user-confirmed feasible envelope; prefer a side when requested without
turning a preference into an unsupported hard prohibition. Update constraints when the
user reports a manual hardware execution was feasible.

For compressible toys, tighter commanded closure may improve grip while the achieved
jaw stops against the toy. Keep those quantities distinct. Respect actual motor/control
limits and soft-body numerics; “the toy will not break” does not imply infinite torque,
zero opening, or that a solver inversion proves the real toy is unclampable. Check both
jaw contacts, slip, lift, containment/support, detach and retraction, not just the lift.
A rim-spanning rest and small vibrations are valid when the task permits them. Choose a
finite post-release window and tolerances from task scale; record them, not an arbitrary
zero-velocity requirement.

## Small physics probes before expensive trials

Separate settling, contact response, short lift, transfer and release probes. Verify
signed net contact force, gravity direction and an elementary support case when a soft
object behaves implausibly. Track element inversion/Jacobian, penetration and momentum
or force residuals as appropriate. Visual shell agreement and lack of self-intersection
alone do not prove constitutive validity. Do not tune stiffness/friction endlessly around
an implementation error. If a solver patch is needed, isolate its build, record source/
binary hashes, validate a minimal reproducer and rerun affected seeds; old trajectories
do not acquire new validation by loading the patched engine.

Inspect velocity/acceleration and torque at physics/controller substeps, not only camera
frames. The case's 25 Hz outputs hid much larger inter-frame velocity spikes under held
actions. Distinguish outer action, inner target and achieved joint state, and verify actual
replay under the intended zero-order hold or causal interpolator. Smooth rendering is
not evidence that the real controller can reproduce it; future command interpolation
must not enter a supposedly causal controller.

## Reuse tiers and their limits

| Derivative | Reuse | Check anew |
| --- | --- | --- |
| Color/light only | motion, contact, release and collision evidence | changed sensor visibility, semantic cues, renderer settings and label completeness |
| External camera | physical trajectory | mount/envelope if applicable, calibration, occlusion and evidence before approach |
| Removing distractors | prior path if removed items provided no support/contact | target/container/support retained, semantic text and affected visibility |
| Symmetric layout/trajectory transform | contact if robot/task symmetry and gravity are preserved | FK/limits, all obstacles, camera/cable, boundaries and actual transformed states |
| IK/time-warp derivative | seed geometry and local contact reference | continuous retargeting, speed/limits, support/clearance; dynamics only within justified bounds |
| New grasp, object geometry, friction, mass or support | unaffected assets only | contact/release and relevant physics |

An arbitrary rigid transform is not a robot symmetry: translating a fixed-base arm's
whole path or tilting gravity does not inherit dynamics. Changed timing can invalidate
force margins even when the Cartesian path is unchanged. Appearance glass changes
rendering only unless mass/friction/shape are also changed; label that scope.

Store seed ID/hash, transform/time map, validation level, inherited report hashes,
per-candidate checks and residuals. A per-episode `task_success` acceptance check may
combine justified inherited evidence and cheap checks; its report must state that, not
claim a fresh simulation. Review representative mechanisms/seeds and newly exposed
views; do not require expensive full physics of every texture derivative.
