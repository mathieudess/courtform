# CourtForm

A small client-side planner for fitting roundnet courts inside a rectangular field.

The app is static: `index.html` runs the layout math directly in browser-side JavaScript. It can be deployed on GitHub Pages, Netlify, Cloudflare Pages, or any other static host.

## Run locally

```powershell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## What it does

- Adjust field width, field length, sideline margin, and minimum center distance.
- Tune the painted court radii in the settings popover without cluttering the main controls.
- Pick grid, hex rows across the width, or hex columns up the length from one layout selector.
- Highlight the best layout by court count, using the lowest overlap area as the tie-breaker.
- Spread courts across the available center zone while keeping center distances at or above the selected minimum.
- Show overlap as a percentage of total court area and report the actual minimum center spacing.
- Print a visualization-ready board with the court drawing, legend, and draw recipe.
- Display outer measurement guides for the first setup marks needed to repeat the layout on the field.
