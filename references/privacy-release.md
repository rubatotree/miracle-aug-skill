# Privacy-aware source branches and releases

Redaction is disabled by default. Do not infer a redaction requirement from windows,
recognizable surroundings, public/private upload, or the presence of this reference.
Preserve the reconstructed appearance unless the user explicitly asks for redaction.
An existing request persists for its project; it is not a default for other inputs.
Do not introduce a privacy approval gate for a project without such a request.

Apply the user's stated privacy scope to every shared artifact, including private
repositories when the user asks for redaction. A private destination is not a substitute
for requested redaction. Preserve original working evidence locally; create a separate
shareable scene branch and record its hash and transformation.

For exterior redaction, decide whether the request permits coarse pixelation or needs
synthetic replacement. Weak blur can retain skyline/geolocation cues. The implemented
case removed the exterior photo and inferred city panorama entirely, replacing them
with an opaque generated mosaic in all relevant materials. This knowingly changes
exterior appearance and lighting; label it as privacy preprocessing. Keep an unshared
reference-matching checkpoint for reconstruction evaluation.

Redaction must cover camera, reflection, refraction/transmission and indirect-light
paths. Check mirrors, glass and reverse cameras. Reopen the saved blend and inspect
image datablocks, unused/packed images, compositor/view-layer nodes, world textures,
linked assets, text blocks and external file references. Turning off one visible
photo plane does not remove its original pixels from a packed scene.

For a scene release, use an explicit dependency whitelist and a relocated smoke test.
When redaction is requested, exclude targeted original pixels from source videos,
panoramas, old overlays, hidden previews, thumbnails and unrelated checkpoint blends.
Without that request, required scene textures keep their original appearance.
Credentials, server
proxy configs, HF cache, shell histories and personal machine paths do not belong
in a GitHub skill or shared example. Keep asset attribution for redistributable models.

Bind `privacy_release.json` to scene/code/material hashes and actual inspected render
evidence. A stale boolean from an earlier scene must not release a changed artifact.
Recheck new asset variants if they can introduce sensitive imagery. All generated
episodes must carry verified privacy labels consistent with the source branch.

If an old unsanitized run already exists, hold its upload and stop only that project's
workers if necessary. Keep it separate from the new sanitized session; never mix its
cache or review outputs. If a test upload already exposed data, inspect and remove only
the affected project-owned artifacts within the user's authorized privacy repair scope.
Do not claim that deleting a repository proves provider backups or uncommitted storage
were erased. Record the cleanup and any remaining uncertainty honestly.

Before distributing this skill, run its tests and inspect the release inventory.
Ship generic text/code and fully synthetic tests; optional reviewed example renders
can be included under an explicit file/hash allowlist with license/source attribution.
Apply privacy checks to those examples only to the extent requested by their user.
The skill must work without real-scene examples. GitHub publication remains distinct from preparing a local
GitHub-ready package and needs the user's publication instruction.
