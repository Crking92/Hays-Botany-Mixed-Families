# Mixed Families — existing source and public learner QA (October 30, 2026)

**Migration source integrity: PASS.** Verified all **532** rows from the original transfer manifest against staging Git tree `4591ef892bcf074944a61dd3750794d6206147b1`, with **532/532 exact source blob hashes**, zero missing and zero mismatches. Manifest's original hub snapshot: `515387cbc23b8bf8931141ead9c44c92a7793699`.

| Item | Verified count |
|---|---:|
| Assigned families | 33 |
| Original species | 105 |
| Source text / credit files | 362 |
| Source original photo files | 170 |
| Published species JSON files | 105 |
| Published hosted existing photos | 19 |
| Species with published images | 14 |
| Held source photo metadata references | 152 of 171 |

The public learner data index matches the installed published species JSON files; its gallery index photo total matches the actual published media file count as inspected October 30, 2026. No new photo collection, species edits, source-photo deletion, or legacy hub mutation occurred.

This checkpoint adds a read-only local + live Pages verification script. The script verifies each publication file, associated photo Git blob SHA, rights metadata and photo credits. **Do not claim the end-to-end live URL test has passed until its workflow run is successful.**

Important distinction: historical held photo bytes are in a publicly readable Git repository and may require later provenance remediation; the Pages rights-filter itself does not restrict source/history access. Existing source archival preservation is complete separately from future photo licensing and field-ready anatomy improvements. Old text-only workflow failures are safety blocks, not missing source data. Future species writes route to this family's staging branch, the original hub stays read-only, and automations stay paused.
