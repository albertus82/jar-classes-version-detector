import os
import unittest
import zipfile

import jarver

TESTS_DIR = os.path.dirname(__file__)


class TestJarver(unittest.TestCase):

    def test_analyze_contents(self):
        with zipfile.ZipFile(os.path.join(TESTS_DIR, "dummy.jar")) as file:
            self.assertEqual(jarver.analyze_contents(file), {
                (57, 0): ["DummyClass13.class"],
                (56, 0): ["DummyClass12.class"],
                (55, 0): ["DummyClass11.class"],
                (54, 0): ["DummyClass10.class"],
                (53, 0): ["DummyClass9.class"],
                (52, 0): ["DummyClass8.class"],
                (51, 0): ["DummyClass7.class"],
                (50, 0): ["DummyClass6.class"],
                (49, 0): ["DummyClass5.class"],
                (48, 0): ["DummyClass1_4.class"],
                (47, 0): ["DummyClass1_3.class"],
                (46, 0): ["DummyClass1_2.class"],
                (45, 3): ["DummyClass1_1.class"]
            })

    def test_main(self):
        self.assertIsNone(jarver.main([os.path.join(TESTS_DIR, "dummy.jar"), os.path.join(TESTS_DIR, "bad.jar"), os.path.join(TESTS_DIR, "fat.jar"), "https://repo1.maven.org/maven2/junit/junit/4.12/junit-4.12.jar"]))


if __name__ == '__main__':
    unittest.main()
