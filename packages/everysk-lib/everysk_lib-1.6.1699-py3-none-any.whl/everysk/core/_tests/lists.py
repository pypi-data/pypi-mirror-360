###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from math import ceil

from everysk.core.unittests import TestCase
from everysk.core.lists import split_in_slices, slices, sort_list_dict

###############################################################################
#   Lists Module Test Case
###############################################################################
class SplitInSlicesTestCase(TestCase):

    def test_split_in_slices_valid_cases(self):
        self.assertEqual(split_in_slices(1, 2), [slice(0, 1)])
        self.assertEqual(split_in_slices(2, 2), [slice(0, 2)])
        self.assertEqual(split_in_slices(3, 2), [slice(0, 2), slice(2, 3)])
        self.assertEqual(split_in_slices(5, 2), [slice(0, 2), slice(2, 4), slice(4, 5)])
        self.assertEqual(split_in_slices(6, 2), [slice(0, 2), slice(2, 4), slice(4, 6)])

    def test_split_in_slices_invalid_cases(self):
        self.assertEqual(split_in_slices(0, 2), [])
        self.assertEqual(split_in_slices(-1, 2), [])
        self.assertEqual(split_in_slices(2, 0), [])
        self.assertEqual(split_in_slices(2, -1), [])
        self.assertEqual(split_in_slices(0, 0), [])

    def test_split_in_slices_large_input(self):
        size = 100
        chunk_size = 25
        result = split_in_slices(size, chunk_size)
        expected = [slice(0, 25), slice(25, 50), slice(50, 75), slice(75, 100)]
        self.assertEqual(result, expected)

    def test_split_in_slices_non_divisible(self):
        size = 10
        chunk_size = 3
        result = split_in_slices(size, chunk_size)
        n = ceil(size / chunk_size)
        k, m = divmod(size, n)
        expected = [
            slice(i * k + min(i, m), (i + 1) * k + min(i + 1, m))
            for i in range(n)
        ]
        self.assertEqual(result, expected)

class SlicesTestCase(TestCase):

    def test_2(self):
        lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertListEqual(
            slices(lst, 2),
            [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]
        )

    def test_3(self):
        lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertListEqual(
            slices(lst, 3),
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]
        )

class SortListDictTestCase(TestCase):

    def test_one_key(self):
        lst = [
            {'a': 4},
            {'a': 2},
            {'a': 3},
            {'a': 6},
            {'a': 1},
            {'a': 5},
        ]
        self.assertListEqual(
            sort_list_dict('a', lst=lst),
            [{'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}, {'a': 5}, {'a': 6}]
        )

    def test_two_key(self):
        lst = [
            {'a': 2, 'b': 4},
            {'a': 2, 'b': 3},
            {'a': 2, 'b': 2},
            {'a': 2, 'b': 6},
            {'a': 2, 'b': 1},
            {'a': 2, 'b': 5},
        ]
        self.assertListEqual(
            sort_list_dict('a', 'b', lst=lst),
            [
                {'a': 2, 'b': 1},
                {'a': 2, 'b': 2},
                {'a': 2, 'b': 3},
                {'a': 2, 'b': 4},
                {'a': 2, 'b': 5},
                {'a': 2, 'b': 6}
            ]
        )

    def test_three_key(self):
        lst = [
            {'a': 2, 'b': 1, 'c': 1},
            {'a': 2, 'b': 1, 'c': 6},
            {'a': 2, 'b': 1, 'c': 4},
            {'a': 2, 'b': 1, 'c': 2},
            {'a': 2, 'b': 1, 'c': 5},
            {'a': 2, 'b': 1, 'c': 3},
        ]
        self.assertListEqual(
            sort_list_dict('a', 'b', 'c', lst=lst),
            [
                {'a': 2, 'b': 1, 'c': 1},
                {'a': 2, 'b': 1, 'c': 2},
                {'a': 2, 'b': 1, 'c': 3},
                {'a': 2, 'b': 1, 'c': 4},
                {'a': 2, 'b': 1, 'c': 5},
                {'a': 2, 'b': 1, 'c': 6}
            ]
        )
