import os
import unittest
import zipfile

import jarver

TESTS_DIR = os.path.dirname(__file__)


class TestJarver(unittest.TestCase):

    def test_analyze_classes(self):
        with zipfile.ZipFile(os.path.join(TESTS_DIR, "dummy.jar")) as file:
            self.assertEqual(jarver.analyze_classes(file), {(55, 0): ["DummyClass.class"]})

    def test_main(self):
        self.assertIsNone(jarver.main([os.path.join(TESTS_DIR, "dummy.jar")]))


if __name__ == '__main__':
    unittest.main()
