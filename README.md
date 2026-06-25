# CourtForm

A small client-side planner for fitting roundnet courts inside a rectangular field.

The app is static: `index.html` loads Pyodide from a CDN and runs the layout math in Python directly in the browser. It can be deployed on GitHub Pages, Netlify, Cloudflare Pages, or any other static host.

## Run locally

```powershell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## What it does

- Adjust field width, field length, court radius, minimum center distance, and sideline margin.
- Pick grid, hex rows across the width, or hex columns up the length from a single layout control.
- Highlight the best layout by court count, using the lowest overlap area as the tie-breaker.
- Spread courts across the available center zone while keeping center distances at or above the selected minimum.
- Show overlapping court circles when twice the court radius is larger than the actual nearest center spacing.
- Export or copy a CSV list of center coordinates measured from the lower-left corner.
