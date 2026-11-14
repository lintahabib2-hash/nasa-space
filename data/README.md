# data/

Commit only small, licensed snapshots. Link large files from `docs/source-registry.md` instead of committing them.

| Folder | Source ID | Provenance | Owner |
|---|---|---|---|
| `simulated/` | X01 | `simulated` | M2 |
| `nasa/osdr-eda/` | D01 | `nasa_measured` | M4 |
| `nasa/radlab/` | D02 | `nasa_measured` | M4 |
| `nasa/nlsp-bedrest/` | D03 | `analog_measured` | M2 (optional) |
| `nasa/osd-575/` | D06 | `nasa_measured` | M2 (optional) |
| `external/` | E01/E02 | `external_earth` (parser tests only; git-ignored) | M2 / M6 |
| `fallback/` | D01/D02 | Cited static chart, labeled as **not ingested** | M4 |

Rule: never join different populations or locations on timestamp.
