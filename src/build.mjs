// node build.mjs            -> dist/index.html  (mockup: data inside the page, form sends nothing)
// node build.mjs <URL>      -> site/index.html  (live: data and reports through the Apps Script web app)
import fs from 'node:fs';

const url = process.argv[2] || '';
const nm = 'node_modules/';
const read = p => fs.readFileSync(p, 'utf8');
const safe = s => s.replace(/<\/script/gi, '<\\/script');

let html = read('template.html');
const parts = {
  '/*LEAFLET_CSS*/': read(nm + 'leaflet/dist/leaflet.css'),
  '/*LEAFLET_JS*/': safe(read(nm + 'leaflet/dist/leaflet.js')),
  '/*D3_DISPATCH_JS*/': safe(read(nm + 'd3-dispatch/dist/d3-dispatch.min.js')),
  '/*D3_QUADTREE_JS*/': safe(read(nm + 'd3-quadtree/dist/d3-quadtree.min.js')),
  '/*D3_TIMER_JS*/': safe(read(nm + 'd3-timer/dist/d3-timer.min.js')),
  '/*D3_FORCE_JS*/': safe(read(nm + 'd3-force/dist/d3-force.min.js')),
  '/*TOPOJSON_JS*/': safe(read(nm + 'topojson-client/dist/topojson-client.min.js')),
  '/*LAND_JSON*/': read(nm + 'world-atlas/land-50m.json'),
  '/*DATA_JSON*/': url ? '[]' : safe(JSON.stringify(JSON.parse(read('data.json')))),
  '/*DATA_URL*/': url,
};
for (const [k, v] of Object.entries(parts)) {
  if (!html.includes(k)) throw new Error('missing placeholder ' + k);
  html = html.split(k).join(v);
}
const dir = url ? 'site' : 'dist';
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(dir + '/index.html', html);
console.log(dir + '/index.html', (html.length / 1024).toFixed(0), 'KB');
