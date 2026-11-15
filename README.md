# GRMZK Atlas

Field register of the GRMZK research: a map of gromozekas, metal bodies of the industrial past
that outlived their work and stayed among people.

Live on deviniska.com/grmzk-atlas, embedded from this page with `?embed`.

## How it works

- `index.html` is the whole site in one file: Leaflet, the land outline (Natural Earth via world-atlas)
  and the page code are inlined.
- The objects come from the **Atlas** tab of the GRMZK Google Sheet through a Google Apps Script
  web app (`apps-script/Code.gs`). Photos come from the *GRMZK Atlas photos* folder on Google Drive,
  named by code: `GRMZK-4` is the preview, `GRMZK-4a`, `GRMZK-4b`… are the photos.
- Reports sent with the form land on the **Reports** tab and arrive by email.

## Rebuilding index.html

```
cd src
npm install
DATA_URL="https://script.google.com/macros/s/…/exec" npm run live   # live data
npm run mockup                                                       # data from src/data.json, form sends nothing
```

## Previews

Each object can have a drawn preview: a simplified line drawing on the object's dominant colour.
`src/previews/gen.py` draws them (SVG, then PNG through `rsvg-convert`); the site uses the 256 px copies in `previews/`.
The map picks a preview in this order: a file named exactly `GRMZK-N` in the Drive photo folder, then `previews/GRMZK-N.png`, then the first photo.
