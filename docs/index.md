---
title: Vault Study
---

<style>
.hero {
  margin: 1.5em auto 0.5em;
  text-align: center;
}
.hero picture, .hero img {
  display: inline-block;
  max-width: min(100%, 560px);
  height: auto;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}
.elevator {
  text-align: center;
  font-size: 1.15rem;
  color: #444;
  max-width: 580px;
  margin: 0.5em auto 2em;
}
.nav-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}
.nav-cards a {
  display: block;
  padding: 1.1rem 1.2rem;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: transform .15s, border-color .15s, box-shadow .15s;
}
.nav-cards a:hover {
  transform: translateY(-2px);
  border-color: #159957;
  box-shadow: 0 4px 12px rgba(21,153,87,0.10);
}
.nav-cards h3 { margin: 0 0 .35rem; color: #159957; font-size: 1.05rem; }
.nav-cards p  { margin: 0; color: #586069; font-size: .92rem; }
</style>

<p class="hero">
  <picture>
    <source srcset="assets/generated/mechanism-cam-sweep-fdm.webp" type="image/webp">
    <img src="assets/generated/mechanism-cam-sweep-fdm.gif"
         alt="A 1/12-scale vault mechanism: a 120-tooth ring gear oscillates, driving twelve 24-tooth spur gears, which drive twelve racks and pins radially outward and back."
         width="560">
  </picture>
</p>

<p class="elevator">
A hobby project to redesign Adam Savage's miniature bank-vault door
in parametric CAD, with two variants in parallel: a faithful
machined-style rebuild and an FDM-printable redesign.
</p>

<div class="nav-cards">
  <a href="interactive.html">
    <h3>Interactive demo</h3>
    <p>Drag a slider, watch twelve pins extend in unison.</p>
  </a>
  <a href="mechanics.html">
    <h3>How it works</h3>
    <p>Ring → spurs → racks → pins, in 200 words.</p>
  </a>
  <a href="faithful-vs-fdm.html">
    <h3>Faithful vs FDM</h3>
    <p>What we kept, what we changed, why.</p>
  </a>
  <a href="principles.html">
    <h3>Principles</h3>
    <p>Five things this project believes.</p>
  </a>
</div>

## The whole machine in one paragraph

A 120-tooth ring gear sits in the centre of an acrylic puck. Twelve
24-tooth spur gears surround it; each drives a rack-and-pinion that
pushes a locking pin radially outward into the vault frame. A
miniature 3-wheel combination lock is the gatekeeper — dial the
right combination, a bell crank releases the ring gear, and a single
throw of the lever shoots all twelve pins at once. The rest of the
project is dimensions.

## More to dig into

- [The gearing math](gearing-math.html) — module, tooth counts, why
  the 5:1 ratio falls out for free.
- [Why twelve pins?](why-twelve-pins.html) — divisor math and the
  base-12 elegance.
- [The combination lock](combination-lock.html) — watchmaker-scale
  three-wheel mechanism in a 0.75" × 0.5" brass cage.
- [The hinge and frame](hinge-and-frame.html) — heavy-door swing
  kinematics, the clearance problem CAD catches for free.
- [FDM design considerations](fdm-variant.html) — cylinders → hex
  stock, tolerances, layer orientation.
- [Build log](build-log.html) — informal session notes.
- [Sources](sources.html) — the videos, with timestamps.

## Get the files

| Variant | Onshape | MakerWorld | Printables | STEP |
| --- | --- | --- | --- | --- |
| Faithful | _(placeholder)_ | n/a | n/a | [in repo](https://github.com/jmcpheron/vault-study/blob/main/step-source/unauthorized-vault-clone.step) |
| FDM | _(placeholder)_ | n/a | n/a | [in repo](https://github.com/jmcpheron/vault-study/blob/main/step-source/fdm-vault.step) |

## Credit

The mechanism design, the proportions, the gear math — all
[Adam Savage](https://www.tested.com/)'s work on the Tested YouTube
channel. This site is an independent CAD reinterpretation for
educational and hobby purposes. Full attribution in
[ACKNOWLEDGMENTS.md](https://github.com/jmcpheron/vault-study/blob/main/ACKNOWLEDGMENTS.md).
