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
  margin: 0.5em auto 1em;
}
.try-model {
  text-align: center;
  color: #586069;
  max-width: 580px;
  margin: 0 auto 2em;
  font-size: .95rem;
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
.post-list h3 { margin-bottom: .1rem; }
.post-list .post-date { color: #586069; font-size: .88rem; }
</style>

<p class="hero">
  <picture>
    <source srcset="{{ 'assets/generated/mechanism-cam-sweep-fdm.webp' | relative_url }}" type="image/webp">
    <img src="{{ 'assets/generated/mechanism-cam-sweep-fdm.gif' | relative_url }}"
         alt="A 1/12-scale vault mechanism: a 120-tooth ring gear oscillates, driving twelve 24-tooth spur gears, which drive twelve racks and pins radially outward and back."
         width="560">
  </picture>
</p>

<p class="elevator">
We're modeling Adam Savage's miniature bank-vault door in Onshape —
open the document and play with it — and converting it into a
parametric design an FDM printer can build.
</p>

<p class="try-model">
<strong>Try the model:</strong>
<a href="https://cad.onshape.com/documents/eaf3e87c1faae12ad867b335/w/83a96bb8921d1af3abd7aecd/e/9db299b535aaeded5de5120c">faithful in Onshape ↗</a> ·
<a href="https://cad.onshape.com/documents/017898deda56c430272a5497/w/5d7667d0936a708006b152fa/e/8e68069be3521bc23b864206">FDM in Onshape ↗</a> ·
STEP downloads: <a href="https://github.com/jmcpheron/vault-study/tree/main/step-source">step-source/ on GitHub</a>
</p>

## Build blog

The development log, illustrated — exploded views, gear math,
tolerance stack-ups, and the occasional revision Adam makes for us
mid-series.

<div class="post-list" markdown="1">
{% for post in site.posts %}
### [{{ post.title }}]({{ post.url | relative_url }})

<span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>

{{ post.excerpt }}
{% endfor %}
</div>

[All posts]({{ 'build-log/' | relative_url }}) ·
[RSS feed]({{ 'feed.xml' | relative_url }})

## Reference pages

<div class="nav-cards">
  <a href="{{ 'interactive/' | relative_url }}">
    <h3>Interactive demo</h3>
    <p>Drag a slider, watch twelve pins extend in unison.</p>
  </a>
  <a href="{{ 'mechanics/' | relative_url }}">
    <h3>How it works</h3>
    <p>Ring → spurs → racks → pins, in 200 words.</p>
  </a>
  <a href="{{ 'faithful-vs-fdm/' | relative_url }}">
    <h3>Faithful vs FDM</h3>
    <p>What we kept, what we changed, why.</p>
  </a>
  <a href="{{ 'principles/' | relative_url }}">
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

- [Pin travel]({{ 'pin-travel/' | relative_url }}) — how far do the pins extend for a
  given lever throw, with technical drawings and the math.
- [The gearing math]({{ 'gearing-math/' | relative_url }}) — module, tooth counts, why
  the 5:1 ratio falls out for free.
- [Why twelve pins?]({{ 'why-twelve-pins/' | relative_url }}) — divisor math and the
  base-12 elegance.
- [The combination lock]({{ 'combination-lock/' | relative_url }}) — watchmaker-scale
  three-wheel mechanism in a 0.75" × 0.5" brass cage.
- [The hinge and frame]({{ 'hinge-and-frame/' | relative_url }}) — heavy-door swing
  kinematics, the clearance problem CAD catches for free.
- [FDM design considerations]({{ 'fdm-variant/' | relative_url }}) — cylinders → hex
  stock, tolerances, layer orientation.
- [Sources]({{ 'sources/' | relative_url }}) — the videos, with timestamps.

## Get the files

| Variant | Onshape | MakerWorld | Printables | STEP |
| --- | --- | --- | --- | --- |
| Faithful | [open in Onshape ↗](https://cad.onshape.com/documents/eaf3e87c1faae12ad867b335/w/83a96bb8921d1af3abd7aecd/e/9db299b535aaeded5de5120c) | n/a (CAD study) | n/a (CAD study) | [in repo](https://github.com/jmcpheron/vault-study/blob/main/step-source/faithful-vault.step) |
| FDM | [open in Onshape ↗](https://cad.onshape.com/documents/017898deda56c430272a5497/w/5d7667d0936a708006b152fa/e/8e68069be3521bc23b864206) | _(soon)_ | _(soon)_ | [in repo](https://github.com/jmcpheron/vault-study/blob/main/step-source/fdm-vault.step) |

## Credit

The mechanism design, the proportions, the gear math — all
[Adam Savage](https://www.tested.com/)'s work on the Tested YouTube
channel. This site is an independent CAD reinterpretation for
educational and hobby purposes. Full attribution in
[ACKNOWLEDGMENTS.md](https://github.com/jmcpheron/vault-study/blob/main/ACKNOWLEDGMENTS.md).
