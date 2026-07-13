---
title: Pin travel — how far do they go?
---

# Pin travel — how far do they go?

Turn the lever 15°. How far does each pin extend? Eyeballing the
[cam-sweep animation]({{ '/' | relative_url }}), it's a few millimetres — but how
few, and why? This page walks the math.

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/technical-top-view.svg' | relative_url }}"
       alt="Top-down technical drawing of the vault mechanism showing the ring gear pitch diameter (Ø60), spur bolt-circle diameter (Ø72), pin diameter (Ø10), tooth counts (120 ring teeth, 24 spur teeth × 12 spurs), 30° spur spacing, and module 0.5."
       width="640" style="max-width:100%; height:auto;">
</p>

## The rack-and-pinion identity

Imagine unrolling the spur gear's pitch circle into a straight line.
One full rotation unrolls into 2π·r of circumference, where r is the
pitch radius. The rack rides on that unrolled line — so if the spur
spins by θ radians, the rack travels exactly:

```
linear_travel = θ · r
```

That's it. The rack-and-pinion identity. No magic, just an unrolled
circle.

<style>
.pt-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2em;
  align-items: center;
  justify-content: center;
  margin: 1em auto;
  max-width: 640px;
  font-family: -apple-system, system-ui, sans-serif;
}
.pt-controls label { display: flex; align-items: center; gap: 0.4em; }
.pt-controls input[type="range"] { width: 220px; }
.pt-readout {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  min-width: 6ch;
  text-align: right;
}
#pt-svg {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  height: auto;
}
.pt-math-table {
  margin: 1em auto;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}
.pt-math-table th, .pt-math-table td {
  padding: 0.35em 1em;
  border-bottom: 1px solid #e1e4e8;
  text-align: right;
}
.pt-math-table th { text-align: left; color: #586069; font-weight: 600; }
.pt-math-table tr.highlight td { background: #fff5ee; font-weight: 600; }
</style>

<div class="pt-controls">
  <label>Ring rotation:
    <input type="range" id="pt-slider" min="-15" max="15" step="0.1" value="0">
    <span id="pt-angle-readout" class="pt-readout">0.0°</span>
  </label>
  <label>Pin extension:
    <span id="pt-readout" class="pt-readout">0.00 mm</span>
  </label>
</div>

{% include pin-travel-closeup.svg %}

<script>
(function () {
  const SPUR_PITCH_RADIUS_MM = 6.0;
  const RATIO = 5.0;
  const CLAMP_MM = 12.0;

  const slider = document.getElementById('pt-slider');
  const angleR = document.getElementById('pt-angle-readout');
  const pinR   = document.getElementById('pt-readout');
  const rack   = document.getElementById('pt-rackpin');
  const dimT   = document.getElementById('pt-active-dim');
  if (!slider || !rack) return;

  function update() {
    const thetaDeg = parseFloat(slider.value);
    const thetaRad = thetaDeg * Math.PI / 180;
    const dr = thetaRad * RATIO * SPUR_PITCH_RADIUS_MM;
    const drVis = Math.max(-CLAMP_MM * 0.7, Math.min(CLAMP_MM * 0.7, dr));
    rack.setAttribute('transform', 'translate(' + drVis + ' 0)');
    if (angleR) angleR.textContent = thetaDeg.toFixed(1) + '°';
    if (pinR)   pinR.textContent = dr.toFixed(2) + ' mm';
    if (dimT)   dimT.textContent = 'Δr = ' + dr.toFixed(2) + ' mm';
  }
  slider.addEventListener('input', update);
  update();
})();
</script>

The orange dashed line in the close-up marks where the rack runs out
of teeth — roughly 12 mm of engaged travel before the last rack tooth
disengages from the spur. We'll come back to that.

## Plug in the vault numbers

The vault has **module 0.5** gears. The 24-tooth spur has a pitch
diameter of `0.5 × 24 = 12 mm`, so its pitch radius is `r = 6 mm`.

The ring (driver) has 120 teeth; the spur (driven) has 24. The ratio
is `120 / 24 = 5` — every full turn of the ring drives each spur
five full turns.

Chaining the two: if the **ring** rotates by θ radians, each spur
rotates by `5θ` radians, and the rack (driven by the spur) travels:

```
pin_travel_mm = (5 · θ_ring_rad) · r_spur_pitch
              = 5 · θ_ring_rad · 6 mm
              = 30 · θ_ring_rad
```

Thirty millimetres of pin travel per radian of ring rotation. Convert
to degrees:

```
pin_travel_mm = 30 · (π / 180) · θ_ring_deg
              ≈ 0.524 · θ_ring_deg
```

About **half a millimetre of pin extension per degree of ring
rotation**. The reciprocal — about **1.91° of ring rotation per
millimetre of pin extension** — is the useful number if you're
designing a lever's mechanical advantage.

## How that lands at typical lever angles

<table class="pt-math-table">
  <thead><tr><th>Ring rotation</th><th>Pin travel</th></tr></thead>
  <tbody>
    <tr><td>5°</td><td>2.62 mm</td></tr>
    <tr><td>10°</td><td>5.24 mm</td></tr>
    <tr class="highlight"><td>15°</td><td>7.85 mm</td></tr>
    <tr><td>20°</td><td>10.47 mm</td></tr>
    <tr><td>22.9°</td><td>12.00 mm  <em>(rack disengages)</em></td></tr>
    <tr><td>30°</td><td>15.71 mm  <em>(over-travel)</em></td></tr>
    <tr><td>45°</td><td>23.56 mm  <em>(way over-travel)</em></td></tr>
  </tbody>
</table>

The realistic operating range — between the resting position and the
rack's disengagement point — is a ring angle of about ±22°. Adam's
build doesn't show a clean lever-stop angle on camera, but a 15°
throw landing the pins at ~7.85 mm of extension feels about right for
the geometry: that's ~65% of available stroke, well within the
mechanism's design range.

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/pin-travel-diagram.svg' | relative_url }}"
       alt="A single locking pin shown in two positions: at rest (light grey) inside the door body bore, and after a 15° lever throw (dark) extended into the frame receiver. The travel between the two positions is 7.85 mm."
       width="640" style="max-width:100%; height:auto;">
</p>

## Sanity check

The pins are 30 mm long. With 7.85 mm of travel from a 15° throw,
the pin starts proud at rest and ends well into the frame receivers.
Plenty of engagement, plenty of margin before the rack disengages.
The numbers fit the design.

## What about the FDM variant?

It's the same. The kinematic identities are **gear-math invariants**
— they depend only on the module, the tooth counts, and the ratio.
The FDM redesign swaps cylinders for hex stock and adjusts
tolerances for printer realities, but it preserves the gears. So
every number on this page applies identically to the FDM build. See
[the FDM design considerations]({{ '/fdm-variant/' | relative_url }}) for what *does*
change.

## See also

- [The gearing math]({{ '/gearing-math/' | relative_url }}) — where the 5:1 ratio comes
  from and why module matters more than diameter.
- [Interactive mechanism]({{ '/interactive/' | relative_url }}) — the full assembly,
  driven by a slider. This page is the math behind that demo.
- [Mechanics overview]({{ '/mechanics/' | relative_url }}) — the whole power chain from
  dial to pins.
