import logging
import os
import shutil
import traceback
import sys
import lcbuilder.eleanor
sys.modules['eleanor'] = sys.modules['lcbuilder.eleanor']
import eleanor


class EleanorManager:
    @staticmethod
    def update():
        eleanor_path = os.path.join(os.path.expanduser('~'), '.eleanor')
        try:
            eleanor.update_max_sector()
        except Exception as e:
            traceback.print_exc()
            logging.exception("Can't update ELEANOR max_sector")
            return
        from eleanor.maxsector import maxsector
        for sector in range(1, maxsector + 1):
            sectorpath = eleanor_path + '/metadata/s{:04d}'.format(sector)
            if os.path.exists(sectorpath) and os.path.isdir(sectorpath) and not os.listdir(sectorpath):
                os.rmdir(sectorpath)
            if (not os.path.exists(sectorpath) or not os.path.isdir(sectorpath) or not os.listdir(sectorpath)) \
                    and sector <= maxsector:
                try:
                    eleanor.Update(sector)
                except Exception as e:
                    logging.exception("Can't update ELEANOR sector %s", maxsector)
                    if os.path.exists(sectorpath):
                        shutil.rmtree(sectorpath)
                    break