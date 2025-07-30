import unittest

from dict_toolset import compare
from dict_toolset._compare import DifferenceType


class CompareTest(unittest.TestCase):

    def test_c1(self):
        result = list(compare({
            "name": "Supi",
            "sub": {
                "name": "SupiSub"
            }
        }, {
            "name": "Supi",
            "sub": {
                "name": "SupiSub",
                "content": "Sdjjahsdh"
            }
        }))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "MISSING sub.content IN A: Sdjjahsdh")

    def test_c2(self):
        result = list(compare({
            "name": "Supi",
            "subs": [
                "str"
            ]
        }, {
            "name": "Supi",
            "subs": [
                "str",
                "duf"
            ]
        }))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "MISSING subs[1] IN A: duf")

    def test_c3(self):
        result = list(compare([
            {
                "id": "djajshd",
                "name": "supi",
                "kacki": "dsadasdasd"
            }
        ], [
            {
                "id": "djajshd",
                "name": "supi",
                "kacki": "dsadasdasd"
            },
            {
                "id": "sdajsjdhas",
                "name": "supi2",
                "kacki": "dsad2asdasdd"
            },
        ]))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "MISSING [id=sdajsjdhas] IN A: {'id': 'sdajsjdhas', 'name': 'supi2', 'kacki': 'dsad2asdasdd'}")
