# Routines

A tiny, dependency-free habit & routine tracker that runs entirely in the browser.

## Features

- Add routines and tag them by time of day (morning / afternoon / evening / anytime)
- Check them off for today; a progress ring shows the day's completion
- Automatic streak counting (consecutive days), with the day's best streak summarized
- Filter the list by time of day
- "Reset today" to clear the current day's check-offs
- Data is saved locally in your browser via `localStorage` — no server, no accounts

## Usage

Open `index.html` in any modern browser. That's it.

To serve it locally:

```sh
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Files

- `index.html` — markup
- `styles.css` — styling
- `app.js` — app logic. Pure helpers (date math, streaks, toggling) are exported
  via `module.exports` so they can be unit-tested under Node; the DOM wiring only
  runs in the browser.
