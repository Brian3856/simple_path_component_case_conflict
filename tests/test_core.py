import unittest

from simple_path_component_case_conflict import find_case_conflicts, group_by_casefold


class FindCaseConflictsTests(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(find_case_conflicts([]), [])

    def test_no_conflicts(self):
        paths = ["src/main.py", "src/util.py", "README.md"]
        self.assertEqual(find_case_conflicts(paths), [])

    def test_simple_conflict(self):
        paths = ["src/Main.py", "src/main.py"]
        self.assertEqual(find_case_conflicts(paths), [["src/Main.py", "src/main.py"]])

    def test_conflict_is_sorted_within_group(self):
        paths = ["src/main.py", "src/Main.py"]
        self.assertEqual(find_case_conflicts(paths), [["src/Main.py", "src/main.py"]])

    def test_conflict_in_middle_component(self):
        paths = ["a/B/c", "a/b/c"]
        self.assertEqual(find_case_conflicts(paths), [["a/B/c", "a/b/c"]])

    def test_three_way_conflict(self):
        paths = ["a/b", "A/b", "a/B"]
        self.assertEqual(find_case_conflicts(paths), [["A/b", "a/B", "a/b"]])

    def test_multiple_independent_conflicts(self):
        paths = ["x/Y", "x/y", "p/Q", "P/q"]
        self.assertEqual(
            find_case_conflicts(paths),
            [["P/q", "p/Q"], ["x/Y", "x/y"]],
        )

    def test_separator_is_not_casefolded(self):
        # A path with no separator must not collide with one that has a
        # separator just because the components fold to the same text.
        paths = ["ab", "a/b"]
        self.assertEqual(find_case_conflicts(paths), [])

    def test_unicode_casefold(self):
        # German sharp s casefolds to 'ss', which is the intended behaviour
        # for caseless comparison.
        paths = ["Straße", "STRASSE"]
        self.assertEqual(find_case_conflicts(paths), [["STRASSE", "Straße"]])

    def test_empty_string_does_not_conflict_with_itself(self):
        self.assertEqual(find_case_conflicts([""]), [])

    def test_empty_string_conflicts_with_other_empty_string(self):
        self.assertEqual(find_case_conflicts(["", ""]), [["", ""]])

    def test_duplicate_identical_paths_are_a_conflict(self):
        # Two identical paths are a conflict in the sense that they map to
        # the same location; the function reports them because it groups by
        # casefolded key and a group of size two is returned.
        self.assertEqual(find_case_conflicts(["a", "a"]), [["a", "a"]])

    def test_accepts_any_iterable(self):
        paths = (p for p in ["a/B", "a/b"])
        self.assertEqual(find_case_conflicts(paths), [["a/B", "a/b"]])


class GroupByCasefoldTests(unittest.TestCase):
    def test_groups_preserve_original_strings(self):
        groups = group_by_casefold(["a/B", "a/b", "c"])
        self.assertEqual(
            groups,
            {"a/b": ["a/B", "a/b"], "c": ["c"]},
        )

    def test_empty_input(self):
        self.assertEqual(group_by_casefold([]), {})

    def test_empty_string_key(self):
        self.assertEqual(group_by_casefold([""]), {"": [""]})

    def test_insertion_order_is_first_appearance(self):
        groups = group_by_casefold(["B", "a", "A"])
        self.assertEqual(list(groups.keys()), ["b", "a"])


if __name__ == "__main__":
    unittest.main()
