"""Test wrappers module contents’ behavior"""

from ncw import wrappers

from . import test_base as tb


class EnforceDictOrList(tb.VerboseTestCase):
    """enforce_dict_or_list() module-level function"""

    def test_with_list(self):
        """call with a list"""
        original_list = [1, 2, 5]
        self.assertIs(wrappers.enforce_dict_or_list(original_list), original_list)

    def test_with_dict(self):
        """call with a dict"""
        original_dict = {"a": 1, "c": 3}
        self.assertIs(wrappers.enforce_dict_or_list(original_dict), original_dict)

    def test_with_scalar(self):
        """call with a scalar value"""
        self.assertRaisesRegex(
            TypeError,
            "^expected dict or list$",
            wrappers.enforce_dict_or_list,
            "arbitrary scalar value",
            error_message="expected dict or list",
        )


class Structure(tb.VerboseTestCase):
    """Structure class initialized with defaults
    (separator=".")
    """

    def setUp(self):
        """Initialize an immutable instance"""
        super().setUp()
        self.original_data = tb.load_testdata(tb.SIMPLE)
        self.structure = wrappers.Structure(self.original_data)

    def test_init_from_instance(self):
        """Initialize from another instance"""
        second_instance = wrappers.Structure(self.structure)
        self.assertDictEqual(second_instance.data, self.structure.data)
        self.assertIsNot(second_instance, self.structure)

    def test_attributes(self):
        """attribute access:
        data attribute equals original data but is a different object,
        separator is a dot
        """
        self.assertIsNot(self.structure.data, self.original_data)
        self.assertDictEqual(self.structure.data, self.original_data)
        self.assertEqual(self.structure.parsing_cache.separator, ".")
        self.assertFalse(self.structure.is_mutable)

    def test_repr(self):
        """repr(structure_instance)"""
        self.assertEqual(
            repr(self.structure),
            f"Structure({self.original_data!r}, separator='.')",
        )

    def test_eq(self):
        """equality"""
        second_instance = wrappers.Structure(self.original_data)
        self.assertEqual(second_instance, self.structure)

    def test_ne(self):
        """inequality"""
        second_instance = wrappers.Structure(self.original_data | {"hello": "world"})
        self.assertNotEqual(second_instance, self.structure)

    def test_get_immutable(self):
        """init with defaults and test substrucure access:
        first and second access return the same value
        but not the same object if that object is a collection
        """
        first_get = self.structure.get("metadata.contact")
        second_get = self.structure.get("metadata.contact")
        self.assertIsNot(
            first_get,
            self.original_data["metadata"]["contact"],
        )
        self.assertListEqual(
            first_get,
            self.original_data["metadata"]["contact"],
        )
        self.assertIsNot(first_get, second_get)
        self.assertListEqual(first_get, second_get)

    def test_get_with_default(self):
        """.get_with_default() method"""
        first_get = self.structure.get_with_default(
            "metadata.contact", "random@example.com"
        )
        self.assertListEqual(
            first_get,
            self.original_data["metadata"]["contact"],
        )
        second_get = self.structure.get_with_default(
            "metadata.does.not.exist", "random@example.com"
        )
        self.assertEqual(
            second_get,
            "random@example.com",
        )

    def test_get_with_default_error(self):
        """.get_with_default() method, trying to walk through a leaf"""
        self.assertRaisesRegex(
            TypeError,
            "^Cannot walk through '2025-01-23' using None",
            self.structure.get_with_default,
            "metadata.request.date.null",
            "random@example.com",
        )

    def test_getitem(self):
        """structure_instance[key] capability"""
        self.assertListEqual(
            self.structure["metadata.contact"],
            self.original_data["metadata"]["contact"],
        )

    def test_getitem_different_separator(self):
        """structure_instance[key] capability
        when initialized with a different separator
        """
        slash_separated_structure = wrappers.Structure(
            self.original_data, separator="/"
        )
        self.assertListEqual(
            slash_separated_structure["metadata/contact"],
            self.original_data["metadata"]["contact"],
        )

    def test_iter_canonical_endpoints(self):
        """canonical endpoints"""
        self.assertListEqual(
            list(self.structure.iter_canonical_endpoints()),
            [
                "metadata.contact.0",
                "metadata.contact.1",
                "metadata.request.ref",
                "metadata.request.date",
            ],
        )


class MutableStructure(tb.VerboseTestCase):
    """MutableStructure class initialized with defaults
    (separator=".")
    """

    def setUp(self):
        """Initialize an immutable instance"""
        super().setUp()
        self.original_data = tb.load_testdata(tb.SIMPLE)

    def test_attributes(self):
        """attribute access:
        data attribute is the same object as original data,
        separator is a slash
        """
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertDictEqual(mutable_structure.data, self.original_data)
        self.assertEqual(mutable_structure.parsing_cache.separator, ".")
        self.assertTrue(mutable_structure.is_mutable)

    def test_repr(self):
        """repr(structure_instance)"""
        mutable_structure = wrappers.MutableStructure(self.original_data, separator="$")
        self.assertEqual(
            repr(mutable_structure),
            f"MutableStructure({self.original_data!r}, separator='$')",
        )

    def test_get(self):
        """init substructure access"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        raw_path = "metadata.contact"
        get_results = [mutable_structure.get(raw_path) for _ in range(2)]
        self.assertIs(get_results[0], get_results[1])

    def test_getitem(self):
        """item access"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        raw_path = "metadata.contact"
        getitem_results = [mutable_structure[raw_path] for _ in range(2)]
        self.assertIs(getitem_results[0], getitem_results[1])

    def test_freeze(self):
        """.freeze() method"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        with self.subTest("initial freeze call"):
            self.assertListEqual(
                mutable_structure.freeze(),
                [
                    "MutableStructure instance changed to immutable",
                    "the .get() method will from now on"
                    " return a deep copy of the found substructure",
                ],
            )
        #
        with self.subTest("repeated freeze call"):
            self.assertListEqual(
                mutable_structure.freeze(),
                [
                    "No change, MutableStructure instance had already been immutable",
                ],
            )
        #

    def test_delete_method(self):
        """.delete() method"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertIn("metadata", mutable_structure.data)
        mutable_structure.delete("metadata")
        self.assertNotIn("metadata", mutable_structure.data)

    def test_delete_empty(self):
        """.delete() method"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertRaisesRegex(
            IndexError,
            r"^Minimum one path component is required, but got only \(\)$",
            mutable_structure.delete,
            "",
        )
        mutable_structure.delete("metadata")
        self.assertNotIn("metadata", mutable_structure.data)

    def test_delitem(self):
        """delete through special method __delitem__"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertIn("request", mutable_structure.data["metadata"])
        del mutable_structure["metadata.request"]
        self.assertNotIn("request", mutable_structure.data["metadata"])

    def test_update_method_simple(self):
        """.update() method with a simple item"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertEqual(mutable_structure["metadata.request.ref"], "issue-12345")
        mutable_structure.update("metadata.request.ref", ["item1", "item2"])
        self.assertListEqual(
            mutable_structure["metadata.request.ref"], ["item1", "item2"]
        )

    def test_update_method_fail_on_missing_keys(self):
        """.update() method with fail_on_missing_keys set True"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertEqual(mutable_structure["metadata.request.ref"], "issue-12345")
        mutable_structure.update("metadata.request.ref", 25, fail_on_missing_keys=True)
        self.assertEqual(mutable_structure["metadata.request.ref"], 25)
        self.assertRaisesRegex(
            KeyError,
            "^'response'$",
            mutable_structure.update,
            "metadata.response.ref",
            99,
            fail_on_missing_keys=True,
        )

    def test_update_method_fail_on_empty_path(self):
        """.update() method failing early on an empty path"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertRaisesRegex(
            ValueError,
            "^Cannot modify with an empty path$",
            mutable_structure.update,
            "",
            "x",
        )

    def test_update_method_with_new_substructure(self):
        """.update() method with a new substructure"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertDictEqual(
            mutable_structure["metadata.request"],
            {"ref": "issue-12345", "date": "2025-01-23"},
        )
        mutable_structure.update("metadata.request.requester.name.first", "John")
        self.assertDictEqual(
            mutable_structure["metadata.request"],
            {
                "ref": "issue-12345",
                "date": "2025-01-23",
                "requester": {"name": {"first": "John"}},
            },
        )
        self.assertListEqual(
            list(mutable_structure.iter_canonical_endpoints()),
            [
                "metadata.contact.0",
                "metadata.contact.1",
                "metadata.request.ref",
                "metadata.request.date",
                "metadata.request.requester.name.first",
            ],
        )

    def test_setitem(self):
        """update through special method __setitem__"""
        mutable_structure = wrappers.MutableStructure(self.original_data)
        self.assertDictEqual(
            mutable_structure["metadata.request"],
            {"ref": "issue-12345", "date": "2025-01-23"},
        )
        mutable_structure["metadata.request"] = 77
        self.assertEqual(mutable_structure.data["metadata"]["request"], 77)
