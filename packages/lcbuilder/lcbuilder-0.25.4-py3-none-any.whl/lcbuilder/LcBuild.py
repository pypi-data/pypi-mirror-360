class LcBuild:
    """
    Used as output of the LcBuilder.build method to unify the returned variables
    """
    def __init__(self, lc, lc_data, star_info,
                 transits_min_count: int,
                 detrend_period: float | None,
                 authors: list[str] | None,
                 cadences: list[int] | None,
                 sectors: list[int] | set[int] | None,
                 sources: list[str] | set[str] | None,
                 apertures: dict = None, sectors_to_start_end_times: dict = None):
        self.lc = lc
        self.lc_data = lc_data
        self.star_info = star_info
        self.transits_min_count = transits_min_count
        self.detrend_period = detrend_period
        self.authors = authors
        self.cadences = cadences
        self.sectors = sectors
        self.tpf_apertures = apertures
        self.tpf_sources = sources
        self.sectors_to_start_end_times = sectors_to_start_end_times

