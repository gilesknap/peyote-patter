# Peyote Pattern Inline Widget Template

Use this for the interactive inline HTML view (show_widget). The PNG renderer
in png-renderer.md is the primary output — use this only if an inline preview
is also wanted alongside the PNG.

The widget shows the fabric view only (interleaved). The pattern view is better
consumed as a PNG due to its height.

```html
<style>
  .wrap { padding: 12px 8px; font-family: var(--font-sans); }
  .legend { display: flex; gap: 16px; margin-bottom: 14px; flex-wrap: wrap;
    font-size: 13px; color: var(--color-text-secondary); align-items: center; }
  .leg-item { display: flex; align-items: center; gap: 6px; }
  .leg-bead { width: 18px; height: 22px; border-radius: 5px;
    border: 1px solid rgba(0,0,0,0.25); }
  .grid-area { overflow-x: auto; }
  .row-wrap { display: flex; align-items: flex-end; margin-bottom: 2px; }
  .row-label { font-size: 10px; font-weight: 500; color: var(--color-text-secondary);
    text-align: right; padding-right: 5px; white-space: nowrap;
    width: 46px; line-height: 24px; }
  .arrow-cell { width: 20px; text-align: center; font-size: 14px;
    color: var(--color-text-secondary); line-height: 24px; flex-shrink: 0; }
  .beads-row { display: flex; align-items: flex-end; }
  .bead { width: 22px; height: 22px; border-radius: 5px;
    border: 1px solid rgba(0,0,0,0.25);
    display: flex; align-items: center; justify-content: center;
    margin: 1px; box-sizing: border-box; flex-shrink: 0; }
  .bead-P { background: #E8A0A8; }
  .bead-R { background: #C82020; }
  .bead-B { background: #3a3c42; }
  .bead-letter { font-size: 9px; font-weight: 600;
    color: rgba(255,255,255,0.95); text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
  .spacer { width: 24px; flex-shrink: 0; }
</style>
<div class="wrap">
  <div class="legend">
    <div class="leg-item"><div class="leg-bead" style="background:#E8A0A8"></div>P=Pink</div>
    <div class="leg-item"><div class="leg-bead" style="background:#C82020"></div>R=Red</div>
  </div>
  <div class="grid-area" id="pattern"></div>
</div>
<script>
const fabric = [
  // paste fabric rows here as arrays of 0/1
];
const colors = { 0:'bead-P', 1:'bead-R' };
const labels = { 0:'P', 1:'R' };
const SLOT = 24;
const container = document.getElementById('pattern');

fabric.forEach((row, ri) => {
  const N = ri + 1;
  const isOdd = N % 2 === 1;
  const fabCols = isOdd ? [0,2,4,6,8] : [1,3,5,7,9];
  const wrap = document.createElement('div');
  wrap.className = 'row-wrap';

  const lbl = document.createElement('div');
  lbl.className = 'row-label';
  lbl.textContent = N === 1 ? 'R1+2' : N === 2 ? '' : `R${N+1}`;
  wrap.appendChild(lbl);

  const arr = document.createElement('div');
  arr.className = 'arrow-cell';
  arr.textContent = N === 2 ? '' : (isOdd ? '←' : '→');
  wrap.appendChild(arr);

  const beadsRow = document.createElement('div');
  beadsRow.className = 'beads-row';

  // Even rows offset right by one SLOT
  if (!isOdd) {
    const sp = document.createElement('div');
    sp.className = 'spacer';
    beadsRow.appendChild(sp);
  }

  fabCols.forEach((fc, bi) => {
    const val = row[fc];
    const d = document.createElement('div');
    d.className = 'bead ' + colors[val];
    d.innerHTML = `<span class="bead-letter">${labels[val]}</span>`;
    beadsRow.appendChild(d);
    if (bi < fabCols.length - 1) {
      const sp = document.createElement('div');
      sp.className = 'spacer';
      beadsRow.appendChild(sp);
    }
  });

  wrap.appendChild(beadsRow);
  container.appendChild(wrap);
});
</script>
```
