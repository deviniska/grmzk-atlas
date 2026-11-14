/**
 * GRMZK Atlas — data and reports for the map on deviniska.com/grmzk-atlas
 *
 * GET  <web app URL>          -> JSON with all objects from the Atlas tab where On map = yes
 * GET  <web app URL>?fresh=1  -> the same, rebuilt right now (skips the 10-minute cache)
 * POST <web app URL>          -> a report from the site form: a new row on the Reports tab + an email to you
 */

const PHOTO_FOLDER_ID = '1Om3EK8dLYEFPhzGGgHCstC89rmY2uwyO'; // Google Drive: GRMZK Atlas photos
const ATLAS_SHEET = 'Atlas';
const REPORTS_SHEET = 'Reports';
const CACHE_SECONDS = 600;

const STATUS = {
  'reference': 'reference',
  'sleeping': 'sleeping',
  'awakened': 'awakened',
  'reborn': 'reborn',
  'fading': 'fading'
};

// ---------- reading ----------

function doGet(e) {
  const fresh = e && e.parameter && e.parameter.fresh === '1';
  const cache = CacheService.getScriptCache();
  let json = fresh ? null : cache.get('atlas');
  if (!json) {
    json = JSON.stringify({ updated: new Date().toISOString(), objects: buildObjects_() });
    if (json.length < 95000) cache.put('atlas', json, CACHE_SECONDS);
  }
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}

function buildObjects_() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(ATLAS_SHEET);
  const values = sheet.getDataRange().getValues();
  const head = values.shift().map(function (h) { return String(h).trim().toLowerCase(); });
  const col = function (name) { return head.indexOf(name); };
  const C = {
    code: col('code'), name: col('name'), status: col('status'), place: col('place'),
    where: col('location'), lat: col('latitude'), lng: col('longitude'), author: col('author'),
    size: col('size'), description: col('description'), links: col('photo links'),
    credits: col('photo credits'), sources: col('sources'), onMap: col('on map')
  };
  const files = photoIndex_();
  const out = [];

  values.forEach(function (r) {
    const code = String(r[C.code] || '').trim().toUpperCase();
    if (!code) return;
    if (String(r[C.onMap] || '').trim().toLowerCase() !== 'yes') return;
    const status = STATUS[String(r[C.status] || '').trim().toLowerCase()];
    const lat = Number(r[C.lat]), lng = Number(r[C.lng]);
    if (!status || r[C.lat] === '' || r[C.lng] === '' || !isFinite(lat) || !isFinite(lng)) return;

    // photos: files from the folder by letter (a, b, c…), then the links from the Photo links column
    const f = files[code] || { preview: null, letters: {} };
    const urls = Object.keys(f.letters).sort().map(function (l) { return imageUrl_(f.letters[l], 1600); });
    lines_(r[C.links]).forEach(function (u) { urls.push(u); });
    const credits = parseCredits_(r[C.credits]);
    const photos = urls.map(function (u, i) {
      return { url: u, credit: credits[String.fromCharCode(97 + i)] || '' };
    });
    const preview = f.preview ? squareUrl_(f.preview, 320)
      : (Object.keys(f.letters).length ? squareUrl_(f.letters[Object.keys(f.letters).sort()[0]], 320)
      : (photos.length ? photos[0].url : null));

    out.push({
      code: code,
      name: String(r[C.name] || ''),
      status: status,
      place: String(r[C.place] || ''),
      where: String(r[C.where] || ''),
      lat: lat,
      lng: lng,
      author: String(r[C.author] || ''),
      size: String(r[C.size] || ''),
      description: String(r[C.description] || ''),
      photos: photos,
      preview: preview,
      sources: lines_(r[C.sources]),
      onMap: true
    });
  });
  return out;
}

// GRMZK-4.jpg -> preview, GRMZK-4a.jpg / GRMZK-4b.png … -> photos a, b …
function photoIndex_() {
  const index = {};
  const it = DriveApp.getFolderById(PHOTO_FOLDER_ID).getFiles();
  while (it.hasNext()) {
    const file = it.next();
    if (file.isTrashed() || String(file.getMimeType()).indexOf('image/') !== 0) continue;
    const base = file.getName().replace(/\.[^.]+$/, '').trim();
    const m = base.match(/^(grmzk-\d+)([a-z])?$/i);
    if (!m) continue;
    const code = m[1].toUpperCase();
    const entry = index[code] || (index[code] = { preview: null, letters: {} });
    if (m[2]) entry.letters[m[2].toLowerCase()] = file.getId();
    else entry.preview = file.getId();
  }
  return index;
}

function imageUrl_(id, width) { return 'https://lh3.googleusercontent.com/d/' + id + '=w' + width; }
function squareUrl_(id, size) { return 'https://lh3.googleusercontent.com/d/' + id + '=w' + size + '-h' + size + '-c'; }

function lines_(v) {
  return String(v || '').split(/\r?\n/).map(function (s) { return s.trim(); }).filter(Boolean);
}

// "a: Jane Doe, CC BY-SA 4.0" -> { a: "Jane Doe, CC BY-SA 4.0" }
function parseCredits_(v) {
  const map = {};
  lines_(v).forEach(function (line) {
    const m = line.match(/^([a-z])\s*[:\-–]\s*(.+)$/i);
    if (m) map[m[1].toLowerCase()] = m[2].trim();
  });
  return map;
}

// ---------- reports from the form ----------

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.website) return json_({ ok: true }); // a bot filled the hidden field
  const missing = ['object', 'where', 'links', 'email'].filter(function (k) { return !String(p[k] || '').trim(); });
  if (missing.length) return json_({ ok: false, error: 'missing: ' + missing.join(', ') });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(p.email))) return json_({ ok: false, error: 'email' });

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName(REPORTS_SHEET).appendRow([
      new Date(), clean_(p.object, 300), clean_(p.where, 300), clean_(p.links, 3000),
      clean_(p.why, 4000), clean_(p.name, 200), clean_(p.email, 200), '', 'new', ''
    ]);
  } finally {
    lock.releaseLock();
  }

  const me = Session.getEffectiveUser().getEmail();
  MailApp.sendEmail({
    to: me,
    replyTo: String(p.email),
    subject: 'GRMZK Atlas: new report — ' + clean_(p.object, 80),
    body: [
      'Object: ' + p.object,
      'Where: ' + p.where,
      'Links:\n' + p.links,
      'Why: ' + (p.why || '—'),
      'Name: ' + (p.name || '—'),
      'Email: ' + p.email,
      '',
      'The report is on the Reports tab: ' + SpreadsheetApp.getActiveSpreadsheet().getUrl()
    ].join('\n')
  });
  return json_({ ok: true });
}

// keep text short and stop it from being read as a formula
function clean_(v, max) {
  let s = String(v || '').trim().slice(0, max);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// Run once from the editor to check the reading part: View → Logs shows how many objects were found.
function testRead() {
  const objects = buildObjects_();
  Logger.log(objects.length + ' objects on the map');
  Logger.log(JSON.stringify(objects[0], null, 2));
}
