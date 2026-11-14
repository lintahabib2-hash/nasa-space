"""Safe statistical states are returned by baseline.get_baseline_result.

Missing current readings produce unknown; limited reference size, zero MAD
and interrupted daily continuity produce explicit insufficient-data states.
No values or timestamps are imputed. See docs/methods-note.md.
"""
