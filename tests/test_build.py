import unittest
import filecmp
import tempfile

from stawp.build import Builder


class TestBuild(unittest.TestCase):

    def build_fixture(self, name, description, options=None):
        with tempfile.TemporaryDirectory() as dest:
            source='tests/fixtures/%s/src' % name
            builder = Builder(dist=dest, base=source, options=options)
            builder.interpret()
            builder.render()
            cmp = filecmp.dircmp(dest, 'tests/fixtures/%s/dest' % name)

            for attr in ['left_only', 'right_only', 'common_funny', 'diff_files', 'funny_files']:
                self.assertEqual(len(getattr(cmp, attr)), 0, 'Failed ' + description + "\n" + attr + " - " + str(getattr(cmp, attr)))

    def test_build_min_copy(self):
        self.build_fixture('minimum-copy', 'copy file only')

    def test_build_min_page(self):
        self.build_fixture('minimum-page', 'minimum configuration with one page')

    def test_build_default(self):
        self.build_fixture('builder', 'default build behavior')

    def test_build_modules_enabled(self):
        self.build_fixture('builder', 'modules enabled', {'enable_modules':'gallery,menu,sitemap'})
