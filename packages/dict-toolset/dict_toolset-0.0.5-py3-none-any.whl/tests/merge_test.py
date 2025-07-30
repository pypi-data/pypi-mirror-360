import unittest

from dict_toolset import merge, compare


class MergeTest(unittest.TestCase):

    def test_c1(self):
        merged = merge({
            "test": "sadhsdha",
            "wann": {
                "name": "kann",
                "index": "sad"
            }
        }, {
            "test": "sadhsdha",
            "wann": {
                "name": "kann2",
                "wisch": "adhsjhkdjkasjkd"
            }
        })

        expected = {
            'test': 'sadhsdha',
            'wann': {
                'name': 'kann', 'index': 'sad', 'wisch': 'adhsjhkdjkasjkd'
            }
        }

        result = compare(merged, expected)
        self.assertEqual(len(list(result)), 0)

    def test_c2(self):
        merged = merge(["name", "wann"], ["test", "wann", "wink"])
        expected = ["name", "wann", "wink"]
        result = compare(merged, expected)
        self.assertEqual(len(list(result)), 0)
