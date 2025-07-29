import unittest
import pandas as pd
import numpy as np
from lightkurve import KeplerLightCurve

from lcbuilder.objectinfo.preparer.MissionLightcurveBuilder import MissionLightcurveBuilder

class TestMissionLightcurveBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = MissionLightcurveBuilder()

    def test_append_lc_data(self):
        author = "test_author"
        cadence = 120
        lc = None
        lc_data = None
        sources = None
        apertures = {}
        sectors = []
        sectors_to_start_end_times = {}
        new_lc = KeplerLightCurve(time=[0.5, 1.5], flux=[0.05, 0.15])
        new_lc_data = pd.DataFrame({'time': [1, 2, 3], 'flux': [0.1, 0.2, 0.3]})
        new_source = "new_source"
        new_apertures = {'aperture1': np.array([1, 2, 3])}
        new_sectors = [1, 2]
        new_sectors_to_start_end_times = {1: {author: {cadence: (0, 1)}}, 2: {author: {cadence: (1, 2)}}}
        lc, lc_data, sources, apertures, sectors, sectors_to_start_end_times = self.builder._append_lc_data(
            author, cadence, lc, lc_data, sources, apertures, sectors, sectors_to_start_end_times,
            new_lc, new_lc_data, new_source, new_apertures, new_sectors, new_sectors_to_start_end_times
        )
        self.assertIsNotNone(lc)
        self.assertIsNotNone(lc_data)
        self.assertEqual(sources, ["new_source"])
        self.assertIn('aperture1', apertures)
        self.assertEqual(sectors, {1, 2})
        self.assertIn(1, sectors_to_start_end_times)
        self.assertIn(2, sectors_to_start_end_times)
        self.assertTrue((lc.time == sorted(lc.time)).all())
        self.assertTrue((lc_data['time'] == sorted(lc_data['time'])).all())

    def test_append_lc_data_with_existing_data(self):
        author = "test_author"
        cadence = 120
        lc = KeplerLightCurve(time=[4.5, 5.5], flux=[0.05, 0.15])
        lc_data = pd.DataFrame({'time': [4.5, 5.5], 'flux': [0.05, 0.15]})
        sources = ["existing_source"]
        apertures = {1: {author: {cadence: [0, 1, 2]}}}
        sectors = {1}
        sectors_to_start_end_times = {2: {author: {cadence: (0, 100)}}}
        new_lc = KeplerLightCurve(time=[1, 2, 3], flux=[0.1, 0.2, 0.3])
        new_lc_data = pd.DataFrame({'time': [1, 2, 3], 'flux': [0.1, 0.2, 0.3]})
        new_source = "new_source"
        new_apertures = {2: np.array([1, 2, 3])}
        new_sectors = [2]
        new_sectors_to_start_end_times = {1: {author: {cadence: (0, 1)}}, 2: {author: {cadence: (1, 2)}}}
        lc, lc_data, sources, apertures, sectors, sectors_to_start_end_times = self.builder._append_lc_data(
            author, cadence, lc, lc_data, sources, apertures, sectors, sectors_to_start_end_times,
            new_lc, new_lc_data, new_source, new_apertures, new_sectors, new_sectors_to_start_end_times
        )
        self.assertIsNotNone(lc)
        self.assertIsNotNone(lc_data)
        self.assertEqual(sources, ["existing_source", "new_source"])
        self.assertIn(1, apertures)
        self.assertIn(2, apertures)
        self.assertEqual(sectors, {1, 2})
        self.assertIn(1, sectors_to_start_end_times)
        self.assertIn(2, sectors_to_start_end_times)
        self.assertTrue((lc.time == sorted(lc.time)).all())
        self.assertTrue((lc_data['time'] == sorted(lc_data['time'])).all())

if __name__ == '__main__':
    unittest.main()