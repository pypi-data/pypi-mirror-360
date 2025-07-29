from astropy.coordinates import SkyCoord
from astroquery.mast import Catalogs

from lcbuilder.star.TicStarCatalog import TicStarCatalog
import astropy.units as u
from astroquery.vizier import Vizier
import foldedleastsquares as tls


class KicStarCatalog(TicStarCatalog):
    def __init__(self):
        super().__init__()

    def catalog_info(self, id):
        """Takes KIC_ID, returns stellar information from online catalog using Vizier"""
        if type(id) is not int:
            raise TypeError('KIC_ID ID must be of type "int"')
        star_data = ([0, 0], None, None, None, None,
                     None, None, None, None, None, None, None, None, None, None, None, None,
                     None, None, None, None, None, None, None)
        columns = ["RAJ2000", "DEJ2000"]
        ra = None
        dec = None
        kic_catalog_query = Vizier(columns=columns).query_constraints(KIC=str(id), catalog="V/133")
        if len(kic_catalog_query) > 0:
            result = (kic_catalog_query[0].as_array())
            ra = result[0]["RAJ2000"]
            dec = result[0]["DEJ2000"]
        ticid = None
        if ra is not None and dec is not None:
            query_region_result = Catalogs.query_region(
                SkyCoord(ra, dec, unit="deg"),
                radius=100*u.arcsec, #arcsecs
                catalog="TIC"
            )
            if len(query_region_result) > 0:
                ticid = int(query_region_result[0]["ID"])
        if ticid is not None:
            star_data = super().catalog_info(ticid)
        else:
            columns = ["Teff", "log(g)", "Rad", "E_Rad", "e_Rad", "Mass", "E_Mass", "e_Mass", "_RA", "_DE"]
            catalog = "J/ApJS/229/30/catalog"
            kic_catalog_query = Vizier(columns=columns).query_constraints(KIC=str(id), catalog=catalog)
            if len(kic_catalog_query) > 0:
                result = (kic_catalog_query[0].as_array())
                Teff = result[0]["Teff"]
                logg = result[0]["log_g_"]
                radius = result[0]["Rad"]
                radius_max = result[0]["E_Rad"]
                radius_min = result[0]["e_Rad"]
                mass = result[0]["Mass"]
                mass_max = result[0]["E_Mass"]
                mass_min = result[0]["e_Mass"]
                ra = result[0]["_RA"]
                dec = result[0]["_DE"]
                lum = self.star_luminosity(Teff, radius)
                ld, mass, mass_min, mass_max, radius, radius_min, radius_max = tls.catalog_info(KIC_ID=id)
                columns = ["Vmag", "Jmag", "Kmag", "Hmag", "kepmag", "[Fe/H]"]
                catalog = "V/133/kic"
                result = (
                    Vizier(columns=columns)
                        .query_constraints(KIC=id, catalog=catalog)[0]
                        .as_array()
                )
                v = result[0]["Vmag"] if "Vmag" in result[0].dtype.names else None
                j = result[0]["Jmag"] if "Jmag" in result[0].dtype.names else None
                k = result[0]["Kmag"] if "Kmag" in result[0].dtype.names else None
                h = result[0]["Hmag"] if "Hmag" in result[0].dtype.names else None
                kp = result[0]["kepmag"] if "kepmag" in result[0].dtype.names else None
                feh = result[0]["__Fe_H_"] if "__Fe_H_" in result[0].dtype.names else None
                star_data = (ld, Teff, lum, logg, None,
                        radius, radius_min, radius_max, mass, mass_min, mass_max, ra, dec, v, None, j, None,
                        h, None, k, None, kp, feh, None)
        return star_data
