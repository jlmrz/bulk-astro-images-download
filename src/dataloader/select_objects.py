
import os
import logging
import numpy as np

from typing import List
from pathlib import Path
from astropy.table import Table


def select_and_save(
        objtype: str,
        savepath: Path,
        nobj: int,
        overwrite: bool=True,
        cols: List[str]=['Z', 'Z_ERR']
) -> None:
   
    objtype = '{:<6}'.format(objtype)

    if not os.path.exists(savepath.parent / 'specObj-dr9.fits'):
        raise FileNotFoundError(
            "Run jobs.sh to download specObj-dr9.fits file from SDSS catalog. " +\
                "For further information see README.md."
            )
    
    logging.info('Loading table data')

    data = Table.read(savepath.parent / 'specObj-dr9.fits', format='fits')

    logging.info('Selecting objects..')
    
    keepcols = ['OBJID', 'PLUG_RA', 'PLUG_DEC', 'CLASS']
    keepcols.extend(cols)
    keepobj = np.where((data["CLASS"] == objtype) & np.all((data["OBJID"] != np.zeros(5)), axis=1))
    data = data[keepcols][keepobj]

    del keepobj, keepcols

    N = len(data)
    indxs = np.sort(np.random.choice(N, size=nobj, replace=False))
    
    logging.info(f'Saving {nobj} randomly chosen objects..')
    data[indxs].write(savepath / f'{objtype.strip()}.fits', format='fits', overwrite=overwrite)

    logging.info(f'{objtype} file is saved.')

