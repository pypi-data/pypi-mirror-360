import unittest

from dict_toolset.tabulate import tabulate
from dict_toolset import compare


class TabulateTest(unittest.TestCase):

    def test_c1(self):
        output = tabulate(
            {
                "a": "a1",
                "b": {
                    "ba": "ba1",
                    "bb": "bb1"
                },
                "c": [
                    {"ca": "ca1"},
                    {"ca": "ca2"},
                ],
                "d": [
                    {"da": "da1"},
                    {"da": "da2"},
                ]
            }, 
            key_converter = lambda x: ".".join(x),
            add_list_index = False
        )

        expected_output = [
            {"a": "a1", "b.ba": "ba1", "b.bb": "bb1", "c.ca": "ca1"},
            {"a": "a1", "b.ba": "ba1", "b.bb": "bb1", "c.ca": "ca2"},
            {"a": "a1", "b.ba": "ba1", "b.bb": "bb1", "d.da": "da1"},
            {"a": "a1", "b.ba": "ba1", "b.bb": "bb1", "d.da": "da2"}
        ]

        check = list(compare(output, expected_output))

        self.assertEqual(len(check), 0)
