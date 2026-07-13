# Style guide

A short editorial guide for the prose in this repo and on its Pages
site. The voice is **casual but the engineering is respected** — we
let ourselves be informal, but the numbers, the citations, and the
mechanism stay sober.

These are the rules. Each one is here because we've watched it
matter. Skipping them is fine if you have a reason; ignoring them
because the prose felt nicer that way is not.

## The seven rules

1. **Active voice, first-person plural.** "We measured the bore at
   18 mm." Not "the bore was measured" and not "Adam measured the
   bore" — the implicit narrator is the project, not a person.

2. **Jokes live in prose, never in code.** Headings, intros, asides
   can be funny. Identifiers, comments, docstrings, dimension tables,
   commit messages, and `params.py` constants stay deadpan. A pun in
   a variable name is a debt that compounds.

3. **No emoji in prose.** One exception: a single load-bearing glyph
   as a section-header marker (a warning ⚠, a link-out ↗). Never
   decorative. Never in body text.

4. **Numbers are sacred.** Any dimension, ratio, or tolerance is
   stated precisely with units. "About / roughly" only appears next
   to an exact figure ("the bore is 17.95 mm — call it 18"). Never
   on its own ("the bore is roughly 18-ish mm" is banned).

5. **Puns must be shorter than the sentence containing them.** If
   the joke takes more words than the point it lands on, cut the
   joke.

6. **Hedge claims, not measurements.** "We *think* the original used
   a 12-tooth pinion" is fine. "The bore is *roughly 18-ish* mm" is
   not. If we don't know the number, we say so and link to where
   the question lives.

7. **Link out, don't paraphrase.** Adam's videos, math identities,
   library docs — when we're citing them, we link. Re-stating
   someone's explanation is how factual drift starts.

## Hero-collision policy

One animated element per viewport on a Pages page. The split:

- **Animated SVG hero** on text/explainer pages — the gear-mesh on
  `gearing-math.md`, the full mechanism on `interactive.md`.
- **GIF hero** on visual/showcase pages — `mechanism-cam-sweep-fdm.gif`
  on `index.md`, `mechanism-exploded-fdm.gif` on `mechanics.md`,
  iso PNGs on `faithful-vs-fdm.md`.

If a page wants both, pick one for above-the-fold and put the other
below an `## H2`.

Blog posts follow the same rule — one animated element per
viewport. Two more post conventions: excerpts on the front-page
stream are text-only (declare `excerpt:` in the front matter; the
default excerpt grabs the post's H1), and every asset or page link
inside a post goes through `relative_url` — posts nest four levels
deep under pretty permalinks, so bare `assets/…` links are bugs.

## Variant-name conventions

- **Faithful** — the CAD reinterpretation of Adam's machined design.
  Lowercase in prose, no scare quotes.
- **FDM** — the 3D-printer-friendly variant. Uppercase, no hyphen.
- The STEP file in `step-source/unauthorized-vault-clone.step` keeps
  its filename as a wink. The neutral name "faithful" appears
  everywhere else.

## What not to commit

- The `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`
  noise (`.gitignore` handles them).
- `/tmp/vaultkit-cache/` — STL cache, regenerated on demand.
- `.DS_Store` files (already in `.gitignore`).
- Frames from intermediate OpenSCAD runs — only commit the final
  GIF + WebP.

## Generated artifacts

`docs/assets/generated/` and `docs/_includes/mechanism-interactive.svg`
are **derived** from the kernel + `params.py`. To regenerate after a
parameter change:

```bash
vaultkit explain render
```

Then commit the regenerated artifacts. (CI auto-commit is wired up
but `workflow_dispatch`-only until the OpenSCAD package on Ubuntu
catches up.)

## Where the principles live

This file is the **contributor** style guide — editorial
conventions, naming, what to commit. The **public-facing** statement
of what the project believes is `docs/principles.md`. They share
spirit but serve different audiences.
