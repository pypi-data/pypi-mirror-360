import logging
from typing import Optional

import lightkurve
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod

from lightkurve import LightCurveCollection

from lcbuilder import constants
from lcbuilder.star.EpicStarCatalog import EpicStarCatalog
from lcbuilder.star.KicStarCatalog import KicStarCatalog
from lcbuilder.star.TicStarCatalog import TicStarCatalog


class LightcurveBuilder(ABC):

    def __init__(self):
        self.star_catalogs = {}
        self.star_catalogs[constants.MISSION_ID_KEPLER] = KicStarCatalog()
        self.star_catalogs[constants.MISSION_ID_KEPLER_2] = EpicStarCatalog()
        self.star_catalogs[constants.MISSION_ID_TESS] = TicStarCatalog()
        self.authors = {}
        self.authors[constants.MISSION_KEPLER] = constants.MISSION_KEPLER
        self.authors[constants.MISSION_K2] = constants.K2_AUTHOR
        self.authors[constants.MISSION_TESS] = constants.SPOC_AUTHOR
        self.authors[constants.MISSION_TESS + "_long"] = constants.TESS_SPOC_AUTHOR

    @abstractmethod
    def build(self, object_info, sherlock_dir, caches_root_dir):
        pass

    @staticmethod
    def sort_lc_data(lcf: LightCurveCollection, mission_prefix: str):
        if mission_prefix == constants.MISSION_ID_KEPLER:
            args = np.argsort(lcf.quarter)
        elif mission_prefix == constants.MISSION_ID_KEPLER_2:
            args = np.argsort(lcf.campaign)
        elif mission_prefix == constants.MISSION_ID_TESS:
            args = np.argsort(lcf.sector)
        return args

    @staticmethod
    def search_lightcurve(target_name: str, mission_prefix: str, mission: str, cadence: int | str, sectors: list,
                          quarters: list, campaigns: list, author: str, download_dir: str, quality_bitmask: int | str,
                          sectors_limit: Optional[int] = None):
        lcf_search_results = lightkurve.search_lightcurve(target_name, mission=mission, exptime=cadence,
                                                          sector=sectors, quarter=quarters,
                                                          campaign=campaigns, author=author, limit=sectors_limit)
        lcf = lcf_search_results.download_all(download_dir=download_dir,
                                              quality_bitmask=quality_bitmask)
        if lcf is None:
            logging.warning(
                f"There are no LightCurves for the given mission {mission}, author {author}, cadence {cadence} and sectors {sectors}")
            return lcf
        else:
            sort_indexes = LightcurveBuilder.sort_lc_data(lcf, mission_prefix)
            return lcf[sort_indexes]

    @staticmethod
    def search_tpf(target_name: str, mission_prefix: str, mission: str, cadence: Optional[int | str],
                   sectors: Optional[list], quarters: Optional[list], campaigns: Optional[list],
                   author: Optional[str], download_dir: Optional[str], quality_bitmask: Optional[int | str],
                   cutout_size: Optional[tuple], sectors_limit: Optional[int] = None):
        tpfs = lightkurve.search_targetpixelfile(target_name, mission=mission, exptime=cadence,
                                                 sector=sectors, quarter=quarters,
                                                 campaign=campaigns, author=author, limit=sectors_limit) \
            .download_all(download_dir=download_dir, cutout_size=cutout_size, quality_bitmask=quality_bitmask)
        if tpfs == None or len(tpfs) == 0:
            tpfs = lightkurve.search_tesscut(target_name, sectors).download_all(download_dir=download_dir,
                                                                                cutout_size=cutout_size,
                                                                                quality_bitmask=quality_bitmask)
        sort_indexes = LightcurveBuilder.sort_lc_data(tpfs, mission_prefix)
        return tpfs[sort_indexes]

    def extract_lc_data_from_df(self, lc_df: pd.DataFrame):
        time = []
        flux = []
        flux_err = []
        background_flux = []
        quality = []
        centroids_x = []
        centroids_y = []
        motion_x = []
        motion_y = []
        if 'time' in lc_df.columns:
            time = lc_df['time'].to_numpy()
        if 'flux' in lc_df.columns:
            flux = lc_df['flux'].to_numpy()
        if 'flux_err' in lc_df.columns:
            flux_err = lc_df['flux_err'].to_numpy()
        if 'quality' in lc_df.columns:
            quality = lc_df['quality'].to_numpy()
        if 'centroid_x' in lc_df.columns:
            centroids_x = lc_df['centroid_x'].to_numpy()
        if 'centroid_y' in lc_df.columns:
            centroids_y = lc_df['centroid_y'].to_numpy()
        if 'motion_x' in lc_df.columns:
            motion_x = lc_df['motion_x'].to_numpy()
        if 'motion_y' in lc_df.columns:
            motion_y = lc_df['motion_y'].to_numpy()
        if 'background_flux' in lc_df.columns:
            background_flux = lc_df['background_flux'].to_numpy()
        lc_data = pd.DataFrame(columns=['time', 'flux', 'flux_err', 'background_flux', 'quality', 'centroids_x',
                                        'centroids_y', 'motion_x', 'motion_y'])
        lc_data['time'] = time
        lc_data['flux'] = flux
        lc_data['flux_err'] = flux_err
        if len(background_flux) > 0:
            lc_data['background_flux'] = background_flux
        if len(quality) > 0:
            lc_data['quality'] = quality
        if len(centroids_x) > 0:
            lc_data['centroids_x'] = centroids_x
            lc_data['centroids_y'] = centroids_y
            lc_data['motion_x'] = motion_x
            lc_data['motion_y'] = motion_y
        lc_data.dropna(subset=['time'], inplace=True)
        return lc_data
