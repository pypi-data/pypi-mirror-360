import unittest
import numpy as np
from lcbuilder.helper import LcbuilderHelper

from lcbuilder.lcbuilder_class import LcBuilder
from lcbuilder.objectinfo.MissionObjectInfo import MissionObjectInfo
from lcbuilder import constants
from lcbuilder.tests.test_lcbuilder_abstract import TestsLcBuilderAbstract


class TestsLcBuilderMask(TestsLcBuilderAbstract):
    def test_short_cadence_mask(self):
        lc_build_no_mask = LcBuilder().build(
            MissionObjectInfo('all', "TIC 352315023", author=[constants.SPOC_AUTHOR],
                              cadence=[120]), "./")
        lc_build = LcBuilder().build(
            MissionObjectInfo('all', "TIC 352315023", author=[constants.SPOC_AUTHOR],
                              cadence=[120], initial_mask=[[1654, 1655]]), "./")
        self.assertEqual(lc_build.cadence, 120)
        self.assertGreater(len(lc_build_no_mask.lc), len(lc_build.lc))
        self._test_tess_star_params(lc_build.star_info)

    def test_short_cadence_high_rms_mask(self):
        sectors = [1, 4, 8, 11]
        lc_build_no_mask = LcBuilder().build(MissionObjectInfo(sectors, "TIC 261136679",
                                                               author=[constants.SPOC_AUTHOR], cadence=[120],
                                                       high_rms_enabled=False, quality_flag=0,
                                                       initial_trim_sectors=2), "./")
        lc_build_mask = LcBuilder().build(MissionObjectInfo(sectors, "TIC 261136679",
                                                            author=[constants.SPOC_AUTHOR], cadence=[120],
                                                       high_rms_enabled=True, high_rms_threshold=5, quality_flag=0,
                                                       initial_trim_sectors=2),
                                          "./")
        lc_build_mask_low = LcBuilder().build(MissionObjectInfo(sectors, "TIC 261136679",
                                                                author=[constants.SPOC_AUTHOR], cadence=[120],
                                                       high_rms_enabled=True, high_rms_threshold=1.15, quality_flag=0,
                                                       initial_trim_sectors=2),
                                              "./")
        self.assertEqual(2, len(lc_build_no_mask.sectors))
        self.assertEqual(lc_build_no_mask.cadence, 120)
        self.assertNotEqual(len(lc_build_no_mask.lc), len(lc_build_mask.lc))
        self.assertTrue(len(lc_build_no_mask.lc) > len(lc_build_mask_low.lc))

    def test_short_cadence_truncate(self):
        lc_build = LcBuilder().build(MissionObjectInfo('all', "TIC 352315023",
                                                       author=[constants.SPOC_AUTHOR], cadence=[120], truncate_border=0.5,
                                                       initial_trim=5, smooth_enabled=True), "./")
        self.assertEqual(lc_build.cadence, 120)
        self.assertEqual(len(lc_build.lc), 791)
        self._test_tess_star_params(lc_build.star_info)

    def test_truncate_borders(self):
        time = np.append(np.arange(0, 13.5, 0.01), np.arange(14.5, 28, 0.01))
        flux = np.ones(2700)
        flux_err = np.full(2700, 0.001)
        time, flux, flux_err = LcbuilderHelper.truncate_borders(time, flux, flux_err, truncate_border=0)
        self.assertEqual(2700, len(time))
        self.assertEqual(2700, len(flux))
        self.assertEqual(2700, len(flux_err))
        time, flux, flux_err = LcbuilderHelper.truncate_borders(time, flux, flux_err, truncate_border=0.5)
        self.assertEqual(2493, len(time))
        self.assertEqual(2493, len(flux))
        self.assertEqual(2493, len(flux_err))


if __name__ == '__main__':
    unittest.main()
