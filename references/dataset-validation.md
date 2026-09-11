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

Production validation checks exact accepted counts by family/intensity/engine, unique
IDs, complete artifacts, finite arrays, synchronized frame/time ranges, source lineage
and declared task validation level. Vectorize inexpensive numeric checks across all rows.
Reuse per-episode render/export receipts instead of decoding and simulating everything
again during each merge. Exercise the official reader on representative episodes,
engines, schema revisions and action boundaries, comparing camera images, state/action
and annotation values against masters. Choose additional decode/review sampling from
observed defects and the user's requirements; do not impose universal all-frame visual
review or compression-error thresholds after the user has waived them. Preserve missing/
corrupt-file, frame-count and temporal integrity checks as applicable.

Full physical seeds and inherited kinematic/appearance derivatives must retain distinct
labels. A success-labelled derivative needs a justified inheritance scope plus relevant
candidate checks; do not describe it as freshly physics-validated. An actual failed task
must not be promoted to success merely to satisfy a count.

Verify actual render metadata agrees with labels: a low-sample preview cannot be
exported as a final high-quality episode. Recompute per-episode and global statistics
for generated signals, including extra features as required by the SDK. Investigate video
compression effects separately when quality is in question or explicitly requested. A
fixed encoder plus known-good export receipts does not require repeated pixel-error QA
on every long-tail sample.

Write a checksummed generation manifest and dataset validation report after all
files are finalized. Upload a complete validated production artifact for its declared scope, with
privacy redaction only where requested. An authorized interim subset can be published
before the full quota is done: bind whole episodes to an immutable subset snapshot and
report its actual counts/distribution, not the final dataset quota claim. Create a new destination or verify an existing
session marker before updating it; never overwrite the source. Honor requested
private/public visibility at creation and verify again after upload. Save remote
commit, inventory and size/hash evidence. Don't claim an upload from successful
authentication or an uncommitted LFS preupload.


## Native compatibility details that mattered in production

Validate the actual installed writer/reader, not just a format sketch. Test image moment
calculations using uint8 extrema: squaring uint8 can overflow and silently destroy RGB
variance. Convert to an appropriate floating type before accumulation if a pinned SDK
needs a localized patch, then record/test that patch. Do not patch current versions merely
because an older version once needed it. Check dependency combinations in an isolated
environment; a successfully imported NumPy/SDK pair may still fail on scalar columns.

When aggregating shards, preserve code-to-name label dictionaries for family, strength,
phase, renderer and quality. Refuse equal numeric IDs with conflicting meanings or
silently reordered categories; allow later-added categories when compatible. Keep each
shard's label provenance and validate actual numeric code ranges. Statistics must describe
the exact selected snapshot, not an earlier/interim or later/full dataset.

Export two observations of the same time as separate native camera streams. Review
mosaics are not replacement training inputs. A requested preview directory should contain
one synchronized MP4 and same-stem JSON per episode, plus an index. Include episode and
candidate IDs, task, source/seed, cameras/order, duration/FPS, engine and real quality,
augmentation parameters, validation scope, units and file hashes. Reuse encoded native
streams or source frames on CPU; do not render again merely to produce inspection videos.

For a gallery with fewer unique examples than requested cells, retain the true count:
use an empty labelled cell or visibly label a repeated example with its source. Preserve
paired-view time and identity across layouts. Excluding an occluded sample from a gallery
does not repair it in the dataset; keep that distinction in the dataset issue record.
