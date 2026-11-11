"""Detect case-insensitive path component collisions.

A path component collision occurs when two distinct path strings differ only
by the case of one or more of their components.  Such a pair is safe on a
case-sensitive filesystem but will silently map to the same location on a
case-insensitive one (macOS by default, Windows, many external drives).

The public entry point is :func:`find_case_conflicts`, which returns a list of
conflict groups.  Each group is a sorted list of the original paths that would
collide.  A path that does not collide with any other path is not returned.

Grouping is done with ``str.casefold`` rather than ``str.lower`` because
casefold is the Unicode-aware operation intended for caseless comparison.
The trade-off is that casefold is slightly more aggressive (for example
the German sharp s ``ß`` casefolds to ``ss``); that matches the behaviour of
case-insensitive filesystems more closely than ``lower`` does, but it can
report a conflict between two names that some filesystems would keep apart.
"""

from __future__ import annotations

from typing import Dict, Iterable, List


def _normalise(path: str) -> str:
    """Return the casefolded key for *path*.

    We casefold component by component so that a separator is never affected
    by the fold.  ``str.casefold`` is defined per code point and does not
    introduce ``/``, but doing it per component makes the intent explicit and
    keeps the key readable when debugging.
    """
    if path == "":
        return ""
    return "/".join(part.casefold() for part in path.split("/"))


def group_by_casefold(paths: Iterable[str]) -> Dict[str, List[str]]:
    """Group *paths* by their casefolded form.

    The returned mapping preserves the original strings, so callers can see
    exactly which spellings collide.  Insertion order of the mapping follows
    first appearance of each key, which keeps output stable for a given input
    order and makes the function pleasant to use in tests.
    """
    groups: Dict[str, List[str]] = {}
    for path in paths:
        key = _normalise(path)
        groups.setdefault(key, []).append(path)
    return groups


def find_case_conflicts(paths: Iterable[str]) -> List[List[str]]:
    """Return groups of paths that collide under case-insensitive matching.

    Only groups with two or more members are returned.  Each group is sorted
    so the result is deterministic regardless of the order in which the input
    was supplied.  The outer list is sorted by the casefolded key as well, so
    callers get a stable, comparable result.

    Empty strings are treated as ordinary (if unusual) components: the empty
    path casefolds to the empty string and will only conflict with itself,
    which is never returned because a single-member group is not a conflict.
    """
    groups = group_by_casefold(paths)
    conflicts = [sorted(members) for members in groups.values() if len(members) > 1]
    conflicts.sort(key=lambda members: _normalise(members[0]))
    return conflicts
