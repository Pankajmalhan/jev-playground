"""Run many calls at once. Used wherever a playground asks Jev about a list of items."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


def map_parallel(fn, items, workers: int = 8) -> list:
    """fn(item) for every item, up to `workers` at a time. Results keep the input order."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, items))
