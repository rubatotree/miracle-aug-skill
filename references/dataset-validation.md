# Dataset contracts and official-reader validation

Inspect the installed dataset SDK and actual source version. Prefer the official
writer/reader for that version. If a custom writer is needed to preserve exact video
encoding or extra features, match the pinned native schema and prove compatibility
through the official loader. A directory of NPZ/Parquet files is not automatically a
LeRobot dataset. Don't install an entire training stack blindly into a shared environment.

The tested project wrote LeRobot v3 and read it with SDK 0.4.3. This is a recorded
compatibility point, not a requirement that every future project use that version.
V3 metadata identifies row ranges and camera video offsets inside shards. Preserve
the source's feature dimensions/names or document intentional transformations. See
[the official format](https://huggingface.co/docs/lerobot/lerobot-dataset-v3).

For each accepted episode provide:

- Synchronized camera frames, state/action tensors with names/units, timestamps,
  validity masks, task ID/instruction and terminal success definition.
- Measured source signals separately from calibrated/synthesized motion. Include
  source-time mapping and per-frame camera/object transforms where generated.
- Source episode/revision/hash, split group, augmentation family/intensity/parameters,
  random seed, asset license provenance and task-check results.
- Actual renderer, settings, quality tier, training sample weight, privacy status and
  semantic limitations. Provide CSV/NPZ joint trajectories when requested.

Treat `T`, state DOF, action DOF, cameras, frame rate and task phases as input-dependent.
Match state/action semantics to the controller: next-position targets differ from
recorded commands and from delta/velocity/torque targets. Do not interpolate discrete
events as continuous joint values. Ensure final invalid targets and action-window
padding do not leak into the next episode.

The portable `validate_episode.py` accepts a schema and canonical JSONL to verify
shapes, finite values, time, camera matrices and explicit next-position alignment.
Run it before native export. It cannot certify a physics/task oracle. Encode these
semantics in the dataset card so a training loader can use the right units/masks.

Validate with an isolated tiny *synthetic* fixture before a long run: at least two
episodes of different lengths, non-default DOF, and multiple cameras when relevant.
Exercise actual SDK writes/reads, tasks, statistics, camera video offsets, terminal
padding and every decoded fixture pixel. Fixture data must be unmistakably marked
and refused by production upload. Don't borrow private unredacted imagery for a
public test fixture.

Production validation must check exact accepted counts by family/intensity/engine,
unique IDs, successful full task checks, complete videos and finite arrays, source
lineage and privacy when required. Decode all videos to verify shape/count/PTS. Read
representative frames at start/middle/end of *every* episode with the official reader
and compare joint/action values, quality/weight fields and camera imagery against the
generated masters. Exercise multi-step action windows at each boundary on fixtures.

Verify actual render metadata agrees with labels: a low-sample preview cannot be
exported as a final high-quality episode. Recompute per-episode and global statistics
for generated signals, including extra features as required by the SDK. Check video
compression effects separately from the exact numerical labels.

Write a checksummed generation manifest and dataset validation report after all
files are finalized. Upload only if production, complete, exact-count, validated and
privacy-released where required. Create a new destination or verify an existing
session marker before updating it; never overwrite the source. Honor requested
private/public visibility at creation and verify again after upload. Save remote
commit, inventory and size/hash evidence. Don't claim an upload from successful
authentication or an uncommitted LFS preupload.
