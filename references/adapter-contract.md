# Project adapter and portable helper boundaries

Keep calibrated scene construction, task/motion logic, rendering and dataset writing
separate. Compose them through plain typed records. Do not copy a hardcoded six-joint
tabletop exporter into a seven-joint or mobile task without adapting its semantics.

A project adapter should expose equivalent operations, with full type hints:

```python
def inspect_source(request: dict[str, object]) -> dict[str, object]: ...
def build_scene(source: dict[str, object], checkpoint: str) -> None: ...
def construct_candidate(candidate: dict[str, object]) -> dict[str, object]: ...
def validate_task(candidate: dict[str, object]) -> dict[str, object]: ...
def render_candidate(candidate: dict[str, object], mode: str) -> dict[str, object]: ...
def export_episode(candidate: dict[str, object], destination: str) -> None: ...
```

These signatures illustrate responsibilities, not a supplied implementation. Write
real scene/task-specific code, test it on the actual input and complete the pipeline.
Keep numerical FK usable outside Blender for fast tests and collision planning.

The canonical per-frame interchange has schema supplied separately:

- `frame_index`, `timestamp`, `observation.state` shape `(D_state,)`, `action` shape
  `(D_action,)`, `action_valid`; dimensions/names/units belong in the schema.
- `cameras[name]`: `intrinsics` shape `(3,3)`, `world_from_camera` shape `(4,4)`, image
  path/key and timestamp. Object transforms use stable IDs and shape `(4,4)`.
- `source_time`, motion provenance, task-success/phase information, actual renderer
  and `training.sample_weight`. Add robot/world velocities only if well defined.

`validate_episode.py` checks numeric/temporal shape and next-position contracts. It
does not infer missing semantics or prove grasp geometry. A schema declares dimensions,
joint names/units, camera keys, FPS or irregular timestamp policy, and action semantics.
Run native SDK validation in addition to this interchange check.

Use `project.py checkpoint --root PROJECT --name scene --report checks/scene.json`
after actual reconstruction. Reports have `passed`, `checks` and project-relative
`artifacts` paths. Required scene checks: `source_match`, `editable_geometry`, `motion`,
`view_coverage`. Required dataset checks: `native_reader`, `video_alignment`,
`trajectory_contract`, `quota_counts`. The helper hashes artifacts and binds reports
to their content; it cannot determine whether a report writer's visual judgment is
true. Include residual metrics and limitations in reports for a reviewer.

After planning, `next` returns one unresolved candidate per deficient stratum. A
single coordinator assigns them to workers; concurrent workers must not mutate the
ledger. Candidate receipts contain `candidate_id`, `plan_sha256`, `outcome` and
`artifacts`. An accepted receipt requires true checks `geometry`, `task_success`,
`visibility`, `render_complete`, `labels`; additionally `privacy` for a privacy request.
Reject receipts give a geometric/semantic reason. Do not record partial preview or
infrastructure failure as an accepted or rejected complete training episode.

```bash
python scripts/project.py record --root PROJECT --receipt checks/candidate_000000.json
python scripts/project.py status --root PROJECT
python scripts/project.py checkpoint --root PROJECT --name dataset --report checks/dataset.json
python scripts/project.py seal --root PROJECT
```

`seal` proves ledger/count/evidence consistency only after the dataset report exists.
Upload remains a project operation requiring the user's destination/visibility and a
verified receipt. A new plan requires a new project/session; edited frozen requests
or modified evidence invalidate resume. Stochastic GPU kernels need not be byte
identical across driver versions; reproducibility requires pinned runtime and logged
settings, plus semantic/numerical tolerances where exact bytes are not promised.
