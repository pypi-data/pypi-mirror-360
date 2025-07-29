import logging
import lightkurve as lk

from lcbuilder.LcBuild import LcBuild
from lcbuilder.objectinfo.preparer.mission_data_preparer import MissionDataPreparer
from lcbuilder.star import starinfo
from lcbuilder.objectinfo.MissionInputObjectInfo import MissionInputObjectInfo
from lcbuilder.objectinfo.preparer.LightcurveBuilder import LightcurveBuilder
import pandas as pd


class MissionInputLightcurveBuilder(LightcurveBuilder):
    def __init__(self):
        super().__init__()

    def build(self, object_info, sherlock_dir, caches_root_dir):
        mission_id = object_info.mission_id()
        sherlock_id = object_info.sherlock_id()
        if isinstance(object_info, MissionInputObjectInfo):
            logging.info("Retrieving star catalog info...")
            mission, mission_prefix, id = MissionDataPreparer.parse_object_id(mission_id)
            if mission_prefix not in self.star_catalogs:
                raise ValueError("Wrong object id " + mission_id)
            star_info = starinfo.StarInfo(sherlock_id, *self.star_catalogs[mission_prefix].catalog_info(id))
        else:
            star_info = starinfo.StarInfo(sherlock_id)
            star_info.assume_model_mass()
            star_info.assume_model_radius()
        logging.info("Loading lightcurve from file " + object_info.input_file + ".")
        df = pd.read_csv(object_info.input_file, float_precision='round_trip', sep=',')
        lc = lk.LightCurve(time=df['time'], flux=df['flux'], flux_err=df['flux_err'])
        lc_data = self.extract_lc_data_from_df(df)
        transits_min_count = 1
        lc = lc.remove_nans()
        return LcBuild(lc, lc_data, star_info, transits_min_count, None, None, None, None, None, None, None)
