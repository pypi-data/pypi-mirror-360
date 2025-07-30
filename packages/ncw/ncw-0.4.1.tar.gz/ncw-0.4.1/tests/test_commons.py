"""ncw.commons module tests"""

from ncw import commons

from . import test_base as tb


class PartialTraverse(tb.VerboseTestCase):
    """partial_tracerse() function"""

    def test_valid_call(self):
        """call with valid data"""
        # config = json.loads(tb.SIMPLE_TESTDATA)
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.partial_traverse(config, (tb.METADATA, tb.REQUEST, tb.REF)),
            (config[tb.METADATA][tb.REQUEST][tb.REF], ()),
        )

    def test_through_a_leaf(self):
        """trying to traverse through a leaf"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            TypeError,
            "^Cannot walk through 'issue-12345' using 'sub-item'",
            commons.partial_traverse,
            config,
            (tb.METADATA, tb.REQUEST, tb.REF, "sub-item"),
        )

    def test_negative_min_remaining_segments(self):
        """trying to use a negative numer of remaining segments"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            ValueError,
            "No negative value allowed here$",
            commons.partial_traverse,
            config,
            (tb.METADATA, tb.REQUEST),
            min_remaining_segments=-1,
        )

    def test_invalid_key(self):
        """trying to use an invalid key"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            KeyError,
            "^'xyz'",
            commons.partial_traverse,
            config,
            (tb.METADATA, tb.REQUEST, "xyz"),
        )

    def test_invalid_key_fail_false(self):
        """trying to use an invalid key"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.partial_traverse(
                config,
                (tb.METADATA, tb.REQUEST, "xyz"),
                fail_on_missing_keys=False,
            ),
            (
                {
                    tb.REF: "issue-12345",
                    tb.DATE: "2025-01-23",
                },
                ("xyz",),
            ),
        )

    def test_through_list_with_invalid_index(self):
        """Call with an indvalid list index"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            TypeError,
            "^list indices must be integers or slices, not ",
            commons.partial_traverse,
            config,
            (tb.METADATA, tb.CONTACT, "first"),
        )


class FullTraverse(tb.VerboseTestCase):
    """full_traverse() function"""

    def test_non_empty(self):
        """non-empty traversal path segments"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.full_traverse(config, (tb.METADATA, tb.CONTACT, 0)),
            "user@example.com",
        )

    def test_full_traverse_empty(self):
        """empty traversal path segmentss"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(commons.full_traverse(config, ()), config)

    def test_through_a_leaf(self):
        """trying to traverse through a leaf"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            TypeError,
            "^Cannot walk through 'issue-12345' using 'abcd'",
            commons.full_traverse,
            config,
            (tb.METADATA, tb.REQUEST, tb.REF, "abcd"),
        )


class TraverseWithDefault(tb.VerboseTestCase):
    """traverse_with_default() function"""

    def test_non_empty(self):
        """non-empty traversal path segments"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.traverse_with_default(
                config, (tb.METADATA, tb.CONTACT, 0), default=999
            ),
            "user@example.com",
        )

    def test_default(self):
        """non-empty traversal path segments"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.traverse_with_default(
                config, (tb.METADATA, "nonexistent"), default=999
            ),
            999,
        )

    def test_through_a_leaf(self):
        """trying to traverse through a leaf"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            TypeError,
            "^Cannot walk through 'issue-12345' using 123",
            commons.traverse_with_default,
            config,
            (tb.METADATA, tb.REQUEST, tb.REF, 123),
            default=True,
        )


class IterPaths(tb.VerboseTestCase):
    """iter_paths() function"""

    def test_non_empty(self):
        """non-empty data structure"""
        data = tb.load_testdata(tb.SIMPLE)
        self.assertListEqual(
            list(commons.iter_paths(data)),
            [
                (tb.METADATA, tb.CONTACT, 0),
                (tb.METADATA, tb.CONTACT, 1),
                (tb.METADATA, tb.REQUEST, tb.REF),
                (tb.METADATA, tb.REQUEST, tb.DATE),
            ],
        )

    def test_partially_empty(self):
        """data structure with empty collections"""
        data = tb.load_testdata(tb.PARTIALLY_EMPTY)
        self.assertListEqual(
            list(commons.iter_paths(data)),
            [
                (tb.METADATA, tb.CONTACT),
                (tb.METADATA, tb.REQUEST),
            ],
        )

    def test_scalar_only(self):
        """data structure consisting of a scalar value only"""
        data = tb.load_testdata(tb.SCALAR_ONLY)
        self.assertListEqual(
            list(commons.iter_paths(data)),
            [],
        )

    def test_empty_collections(self):
        """data structure consisting of an empty collection only"""
        for empty_collection_source in (tb.EMPTY_DICT, tb.EMPTY_LIST):
            with self.subTest("empty collection", source=empty_collection_source):
                data = tb.load_testdata(empty_collection_source)
                self.assertListEqual(
                    list(commons.iter_paths(data)),
                    [],
                )
            #
        #
