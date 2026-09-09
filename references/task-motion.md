# Task-conditioned motion, not just changed pixels

Define the task oracle before augmentation. For pick/place it includes stable rest,
jaw contact, object following the gripper, insertion within a real cavity, release,
and stability after retraction. For pushing it includes support/contact and target
region; for a drawer it includes articulation limits and handle engagement. Describe
the relevant geometry and phases rather than assuming all tasks grasp a plush.

Use the robot's actual DOFs, limits and controller representation. Create independent
contact geometry if visual fur/detail is too expensive, and record approximation/error
bounds. At contact transitions preserve world transforms; interpolate constrained
attachment only when the observed physical event supports it. A smooth blend that
slides through a jaw or wall is still invalid. Keep rigid objects separate from the
robot; soft deformation is object-local and cannot excuse impossible penetration.

Validate every output frame, with extra temporal subdivision near fast movement or
small clearances. Check FK, limits, finite velocities/accelerations, support penetration,
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
