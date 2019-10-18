import unittest
import zipfile

import jarver


class TestJarver(unittest.TestCase):

    def test_analyze_classes(self):
        with zipfile.ZipFile("dummy.jar") as file:
            self.assertEqual(jarver.analyze_classes(file), {(55, 0): ["DummyClass.class"]})

    def test_main(self):
        self.assertIsNone(jarver.main(["dummy.jar"]))


if __name__ == '__main__':
    unittest.main()
