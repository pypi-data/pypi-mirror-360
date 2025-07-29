import os
import shutil
import unittest


class TestsLcBuilderAbstract(unittest.TestCase):
    def tearDown(self) -> None:
        super().tearDown()
        for file in os.listdir(os.path.dirname(__file__)):
            if file.endswith('.png') or file.endswith('.csv') or file.endswith('yaml'):
                os.remove(file)
            elif os.path.isdir(file) and file != "resources":
                shutil.rmtree(file, ignore_errors=True)

    def _get_test_resource_file(self, file_name):
        return os.path.dirname(__file__) + "/resources/" + file_name

    def _test_tess_star_params(self, star_info):
        self.assertAlmostEqual(star_info.mass, 0.47, 1)
        self.assertAlmostEqual(star_info.mass_min, 0.44, 2)
        self.assertAlmostEqual(star_info.mass_max, 0.5, 1)
        self.assertAlmostEqual(star_info.radius, 0.18, 1)
        self.assertAlmostEqual(star_info.radius_min, 0.076, 3)
        self.assertAlmostEqual(star_info.radius_max, 0.284, 3)
        self.assertEqual(star_info.teff, 31000)
        self.assertAlmostEqual(star_info.ra, 300.47, 2)
        self.assertAlmostEqual(star_info.dec, -71.96, 2)

    def _test_kepler_star_params(self, star_info):
        self.assertAlmostEqual(star_info.mass, 0.72, 2)
        self.assertAlmostEqual(star_info.mass_min, 0.22, 2)
        self.assertAlmostEqual(star_info.mass_max, 1.22, 2)
        self.assertAlmostEqual(star_info.radius, 0.734, 2)
        self.assertAlmostEqual(star_info.radius_min, 0.234, 2)
        self.assertAlmostEqual(star_info.radius_max, 1.234, 2)
        self.assertEqual(star_info.teff, 4571)
        self.assertAlmostEqual(star_info.ra, 290.966, 3)
        self.assertAlmostEqual(star_info.dec, 51.50472, 3)

    def _test_k2_star_params(self, star_info):
        self.assertAlmostEqual(star_info.mass, 1.102, 3)
        self.assertAlmostEqual(star_info.mass_min, 0.989, 3)
        self.assertAlmostEqual(star_info.mass_max, 1.215, 3)
        self.assertAlmostEqual(star_info.radius, 1.251, 2)
        self.assertAlmostEqual(star_info.radius_min, 1.012, 3)
        self.assertAlmostEqual(star_info.radius_max, 1.613, 3)
        self.assertEqual(star_info.teff, 6043)
        self.assertAlmostEqual(star_info.ra, 136.573975, 3)
        self.assertAlmostEqual(star_info.dec, 19.402252, 3)
