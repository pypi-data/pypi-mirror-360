"""common constzants and functionality for tests"""

import json
import unittest


SIMPLE = "simple"
PARTIALLY_EMPTY = "partially empty"
SCALAR_ONLY = "scalar only"
EMPTY_DICT = "empty dict"
EMPTY_LIST = "empty list"

# Keys

METADATA = "metadata"
CONTACT = "contact"
REQUEST = "request"
REF = "ref"
DATE = "date"


TESTDATA: dict[str, str] = {
    SIMPLE: """{
      "metadata": {
        "contact": [
          "user@example.com",
          "functional@example.com"
        ],
        "request": {
          "ref": "issue-12345",
          "date": "2025-01-23"
        }
      }
    }
    """,
    PARTIALLY_EMPTY: """{
      "metadata": {
        "contact": [],
        "request": {}
      }
    }
    """,
    SCALAR_ONLY: "2025",
    EMPTY_DICT: "{}",
    EMPTY_LIST: "[]",
}


def load_testdata(name: str):
    """json.loads the specified testdata item"""
    return json.loads(TESTDATA[name])


class VerboseTestCase(unittest.TestCase):
    """TestCase subclass providing the
    full difference output on test failures
    """

    def setUp(self) -> None:
        """set maxDiff None"""
        # pylint: disable=invalid-name ; defined in unittest.TestCase
        self.maxDiff = None
