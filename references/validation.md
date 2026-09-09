# Validation scope for the initial release

The bilingual showcase release passed 14 Python behavioral tests on Python 3.11, including:

- Exact 64/1216 engine allocation for 1280 accepted episodes and deterministic plans.
- Same-stratum rejection/refill, idempotent resume, finite pool exhaustion, no excess
  accepted samples, frozen request/evidence detection and private-release requirements.
- Scene-only initialization that does not authorize generation.
- Variable sequence lengths, 2/7/8 state coordinates, two camera channels, and separate
  recorded-command semantics with a different action dimension.
- Rejection of misaligned actions/timestamps, invalid transforms and missing privacy.
- Local LeRobot v2/v3 metadata and selected Parquet extraction from synthetic episodes,
  including shared-shard offsets and named cameras.
- Deterministic release inventory, hash-bound reviewed images and exclusion of
  scene/video/credential files. Redaction is required only when explicitly requested.

The default request leaves exterior redaction disabled. Tests exercise ordinary
acceptance without privacy redaction, and enforce redaction when the request enables it.

The source helper also resolved a real authenticated HF v3 episode at an immutable
commit and selected its 428 data rows and fixed camera metadata without re-extracting
media. Those private artifacts are not part of this package. The Codex skill structure
validator passed. Relocation is checked by running the helpers from the installed copy.
The README gallery contains actual final-quality renders (Cycles 128-sample limit,
Eevee 64 samples), separately reviewed and checksummed; no public test fixture uses
these images as source data.

These tests verify helper contracts, not automatic reconstruction quality for arbitrary
tasks. The historical scene was inspected and iterated in Blender, but no independent
agent has yet used this packaged skill to rebuild a new robot/task end to end. The
new long rendering batch was still running at extraction time. Policy generalization
has not been demonstrated. Evaluate future changes with new sources and independent
task success measurements, and update this record with actual evidence.
