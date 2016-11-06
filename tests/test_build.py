
import unittest
import filecmp
import classes.build

class TestBuild(unittest.TestCase):

    def build_fixture(self, name):
        dest='/tmp/swp'
        source='tests/fixtures/%s/src' % name
        builder = classes.build.Builder(dist=dest, base=source)
        builder.interpret()
        builder.render()
        cmp = filecmp.dircmp(dest, 'tests/fixtures/%s/dest' % name)
        for attr in ['left_only', 'right_only', 'common_funny', 'diff_files', 'funny_files']:
            self.assertEqual(len(getattr(cmp, attr)), 0, attr + " - " + str(getattr(cmp, attr)))

    def test_build_index(self):
        self.build_fixture('index')

