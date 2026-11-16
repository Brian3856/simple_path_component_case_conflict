# simple_path_component_case_conflict

Detect case-insensitive path component collisions that would break when
moving files between case-insensitive and case-sensitive filesystems.

```python
from simple_path_component_case_conflict import find_case_conflicts

paths = [
    "src/Main.py",
    "src/main.py",
    "docs/readme.md",
]
print(find_case_conflicts(paths))
# [['src/Main.py', 'src/main.py']]
```

## Why this exists

A tree that lives happily on ext4 can become unmergeable the moment it is
copied to APFS or NTFS: two files whose paths differ only by case collide,
and the copy silently overwrites one of them or fails halfway through.  The
problem shows up most often in git checkouts, tarball extractions, and Docker
build contexts, where the offending pair is buried among thousands of paths.

`find_case_conflicts` takes an iterable of path strings and returns a list of
groups.  Each group contains two or more paths that would resolve to the same
location on a case-insensitive filesystem.  Paths that do not collide are not
returned.

The trade-off is deliberate: comparison uses `str.casefold`, not `str.lower`.
Casefold is the Unicode operation intended for caseless matching and it maps
`ß` to `ss`, so `Straße` and `STRASSE` are reported as a conflict.  Some
filesystems would keep those apart.  A stricter byte-wise comparison would
miss real collisions on the filesystems people actually use, so casefold is
the safer default.

## API

- `find_case_conflicts(paths)` — returns a list of lists.  Each inner list is
  a sorted group of colliding paths; the outer list is sorted by the
  casefolded form of the first member.  Only groups of size two or greater
  are returned.
- `group_by_casefold(paths)` — returns a `dict` mapping each casefolded key to
  the original paths that produced it.  Useful when you want to inspect all
  groups, not just the conflicts.

Both functions accept any iterable of strings and never mutate their input.

## The awkward edge

Separators are preserved during casefolding, so `ab` and `a/b` do not
conflict even though the characters fold to the same sequence.  This is
intentional: a path component boundary is not a case distinction, and
treating it as one would produce false positives on unrelated files.

Empty strings are accepted.  A single empty path is not a conflict; two empty
paths are, because they describe the same location.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

