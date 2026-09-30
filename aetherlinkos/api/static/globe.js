// AetherLinkOS — VERATH-ΦΘ globe.
// cobe is loaded from a CDN so the dashboard stays build-step free.
import createGlobe from 'https://esm.sh/cobe@0.6.4';

const canvas = document.getElementById('cobe');

// AetherLink nodes scattered across the globe. The first is the VERATH core,
// tagged `core` so the HTML label can bind to it via CSS anchor positioning.
const NODES = [
  { location: [37.7595, -122.4367], size: 0.08, id: 'core', color: [1, 0.5, 1] }, // VERATH Core (SF)
  { location: [40.7128, -74.006], size: 0.05 },   // New York
  { location: [51.5074, -0.1278], size: 0.05 },   // London
  { location: [35.6762, 139.6503], size: 0.05 },  // Tokyo
  { location: [-33.8688, 151.2093], size: 0.04 }, // Sydney
  { location: [1.3521, 103.8198], size: 0.04 },   // Singapore
  { location: [52.52, 13.405], size: 0.04 },      // Berlin
];

// Live VERATH links radiating out from the core node.
const LINKS = [
  { from: [37.7595, -122.4367], to: [40.7128, -74.006] },
  { from: [37.7595, -122.4367], to: [51.5074, -0.1278] },
  { from: [37.7595, -122.4367], to: [35.6762, 139.6503] },
  { from: [40.7128, -74.006], to: [52.52, 13.405] },
  { from: [35.6762, 139.6503], to: [1.3521, 103.8198] },
  { from: [1.3521, 103.8198], to: [-33.8688, 151.2093] },
];

let phi = 0;
let theta = 0.2;
let width = 0;

// Pointer-drag interaction: spin the globe by hand, ease back to auto-rotate.
let pointerInteracting = null;
let pointerInteractionMovement = 0;
let autoRotate = 0.004;

const onResize = () => {
  width = canvas.offsetWidth;
};
window.addEventListener('resize', onResize);
onResize();

const globe = createGlobe(canvas, {
  devicePixelRatio: 2,
  width: width * 2,
  height: width * 2,
  phi: 0,
  theta,
  dark: 1,
  diffuse: 1.2,
  scale: 1,
  mapSamples: 16000,
  mapBrightness: 6,
  baseColor: [0.32, 0.28, 0.45],
  markerColor: [1, 0.5, 1],
  glowColor: [0.55, 0.4, 0.85],
  offset: [0, 0],
  markers: NODES,
  arcs: LINKS,
  arcColor: [1, 0.5, 1],
  arcWidth: 0.5,
  arcHeight: 0.35,
  markerElevation: 0.02,
  onRender: (state) => {
    if (pointerInteracting === null) {
      phi += autoRotate;
    }
    state.phi = phi + pointerInteractionMovement;
    state.theta = theta;
    state.width = width * 2;
    state.height = width * 2;
  },
});

// ── Pointer interaction ────────────────────────────────────────────────────
const updateMovement = (clientX) => {
  if (pointerInteracting !== null) {
    const delta = clientX - pointerInteracting;
    pointerInteractionMovement = delta / 200;
  }
};

canvas.addEventListener('pointerdown', (e) => {
  pointerInteracting = e.clientX - pointerInteractionMovement * 200;
  canvas.style.cursor = 'grabbing';
});
const endInteraction = () => {
  if (pointerInteracting !== null) {
    phi += pointerInteractionMovement;
    pointerInteractionMovement = 0;
  }
  pointerInteracting = null;
  canvas.style.cursor = 'grab';
};
canvas.addEventListener('pointerup', endInteraction);
canvas.addEventListener('pointerout', endInteraction);
canvas.addEventListener('pointermove', (e) => updateMovement(e.clientX));

// Fade the globe in once the first frame is painted.
requestAnimationFrame(() => (canvas.style.opacity = '1'));

// ── Live kernel status ──────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

async function loadStatus() {
  try {
    const [statusRes, pluginsRes] = await Promise.all([
      fetch('/status'),
      fetch('/plugins'),
    ]);
    const status = await statusRes.json();
    const plugins = await pluginsRes.json();

    const verath = status.verath || status;
    $('st-state').textContent = status.state ?? verath.state ?? 'online';
    const aaiEl = $('st-aai');
    aaiEl.textContent = verath.aai ?? status.aai ?? '—';
    aaiEl.classList.add('ok');
    $('st-class').textContent = verath.aai_class ?? status.aai_class ?? '—';
    $('st-plugins').textContent = (plugins.loaded || []).length;
    $('st-active').textContent = (plugins.active || []).length;
    $('st-hint').textContent = 'Kernel online · auto-refresh 10s';
  } catch (err) {
    $('st-hint').textContent = 'Kernel offline — start with `aetherlinkos serve`.';
  }
}

loadStatus();
setInterval(loadStatus, 10000);
