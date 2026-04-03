# Frontend

This folder contains a very simple standalone frontend for the P2P file sharing
project.

## What it shows

- A client upload panel for `.txt` files
- A small list of connected nodes
- A replication demo where uploaded text appears on every node card

## How to run

Open [index.html](./index.html) directly in a browser.

If you want to serve it locally instead:

```bash
cd frontend
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Notes

This is currently frontend-only and uses browser-side mock data.
When your backend routes are ready, the main place to connect real API calls is
in `app.js`.
