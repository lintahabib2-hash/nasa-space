# Offline QA checklist (2 contrasting scenarios + missing data)

> Owner: Member 6 (Backend, Integration, QA & Deployment)

## Automated (run on every PR and after every deploy)

```bash
cd frontend && npm run build && npm run test:e2e
```

`tests/e2e/offline.spec.ts` loads the production build, waits for the service worker, **turns the network off**, reloads, and checks:

- the app opens and shows "Offline: using saved data"
- crew_01 (stable), crew_02 (gradual drift) and crew_03 (missing data) all render with the right status
- invalid check-in rejected with a message; valid check-in saved; survives an offline reload
- records come back from the IndexedDB mirror after localStorage is wiped
- zero requests leave the app's own origin, zero script errors

`tests/e2e/scenarios.spec.ts` repeats the scenario checks online.

## Manual run on the LIVE URL (before submitting; ideally on a phone too)

1. Open the live URL in a **fresh/incognito window**, network on.
2. Wait for the header badge to read **Offline ready**.
3. Turn the network off (DevTools -> Network -> Offline, or airplane mode). Hard-reload.
4. Tick every row:

| # | Action (network OFF) | Expected | Pass |
|---|---|---|---|
| 1 | Reload the page | Dashboard loads; badge says "Offline: using saved data" | [ ] |
| 2 | Open **Crew 01** (stable) | No indicator is marked Review; provenance says Simulated | [ ] |
| 3 | Open **Crew 02** (gradual drift) | At least one indicator is **Review**; Evidence Drawer shows the reason and the numbers | [ ] |
| 4 | Open **Crew 03** (missing data) | Gaps show **Unknown / Not enough history**, never "no change"; no NaN, null or blank values | [ ] |
| 5 | Switch environment (station / lunar / Mars) | Comms-delay banner changes; NASA environment card still labelled historical instrument data | [ ] |
| 6 | Daily check-in: enter sleep **99**, save | Clear error message; nothing saved | [ ] |
| 7 | Daily check-in: valid values, save | "Check-in saved on this device." appears in History | [ ] |
| 8 | Reload | The check-in is still in History | [ ] |
| 9 | Click an external NASA source link | Browser reports offline for that page (expected); the app itself is unaffected | [ ] |
| 10 | Network ON again, reload | Everything still works; no console errors | [ ] |

## If something fails

| Symptom | Likely cause | Fix |
|---|---|---|
| Badge stuck on "Preparing offline mode" or "Offline mode unavailable" | Not HTTPS, or `sw.js` returned an error | Open `<site>/sw.js`, check the console, confirm the URL is HTTPS |
| Blank page offline, works online | A file is missing from the cache | `npm run build` then `npm run test:e2e`; the test lists what is missing |
| Old version after a deploy | Previous worker still active | Reload twice, or DevTools -> Application -> Service Workers -> Unregister |
| Check-ins gone | Site data cleared | Expected; History export is the backup |
