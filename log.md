# Build log

Reverse-chronological session notes. Newest entries on top. Format
suggestion (not enforced): a date heading, then any mix of what you
modeled, what you learned, what you had to revise, what you got stuck
on. Keep it short — this is for future-you, not for an audience. The
public, illustrated version of this journal is the
[build blog](https://jmcpheron.github.io/vault-study/); this file
stays the terse workshop record.

---

## 2026-07-13 — Refocus: the site is now a build blog

Re-weighted the repo around what it was always about: the Onshape
model first (open it, drag it), the FDM conversion second, the
tooling demoted to a supporting role. The Pages front page is now a
chronological build blog seeded with five posts — kickoff, the
pin-travel math, the 12 mm → 10 mm pin story, the exploded views,
and a new pin-play tolerance stack-up backed by `vaultkit play` and
a generated diagram. Removed the `vault-notes-from-youtube/` scratch
as promised, and fixed every inter-page link the pretty-permalink
setup had silently broken.

## 2026-05-19 — Repo bootstrap

Scaffolded the repo following the Shareable CAD pattern, flattened
for a single project. Two parallel variants (faithful + FDM), both
already seeded as STEP exports in [`step-source/`](step-source/).
Absorbed the `vault-notes-from-youtube/` scratch (since removed)
into the canonical [`specs.md`](specs.md), including the
12 mm → 10 mm pin-diameter revision from part-4 (kept both rows
visible — the lesson is *why* the design is parametric, not just
the latest number). The `vaultkit` Python kernel ships with real
gear math, a `params.py` mirror, and stubs for the heavier
STEP/render pipeline. CI runs lint + tests; Pages deploys from
`/docs`; the auto-commit STEP-artifact workflow is wired up but
`workflow_dispatch`-only until the stubs are real.

What's next: open the two Onshape documents, paste the URLs into
[`cad/faithful/README.md`](cad/faithful/README.md) and
[`cad/fdm/README.md`](cad/fdm/README.md), then start filling in
the explainer pages.

## 2026-05-06 — Kickoff

We watched Adam Savage machine a 1/12-scale bank-vault door on
Tested and couldn't stop thinking about the mechanism: one ring
gear, twelve spur gears, twelve pins, all timed off tooth counts
you can verify by eye. We're rebuilding it in Onshape to learn
assemblies end-to-end — gear relations, rack-and-pinion mates,
sub-assembly patterns — with the gear math checked in code along
the way. Done looks like two things: a public Onshape document
anyone can open and drag, and an FDM-printable conversion anyone
can print. We are intentionally not machining one.
