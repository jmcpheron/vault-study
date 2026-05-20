# Build log

Reverse-chronological session notes. Newest entries on top. Format
suggestion (not enforced): a date heading, then any mix of what you
modeled, what you learned, what you had to revise, what you got stuck
on. Keep it short — this is for future-you, not for an audience. The
[`docs/build-log.md`](docs/build-log.md) Pages page pulls from here.

---

## 2026-05-19 — Repo bootstrap

Scaffolded the repo following the Shareable CAD pattern, flattened
for a single project. Two parallel variants (faithful + FDM), both
already seeded as STEP exports in [`step-source/`](step-source/).
Absorbed the [`vault-notes-from-youtube/`](vault-notes-from-youtube/)
scratch into the canonical [`specs.md`](specs.md), including the
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

## 2026-05-06 — Kickoff (carried over from `vault-notes-from-youtube/log.md`)

<!--
TODO (Jason): write a few lines about why you're starting this and what
you want to get out of it. Things you might capture:
  - What pulled you toward this project right now
  - What you most want to learn (Onshape mates? Gear math? Just modeling
    assemblies end-to-end?)
  - What "done" or "good enough" looks like for you
  - Anything you're intentionally NOT going to worry about
The voice you set here is the voice the rest of the log will inherit.
-->
