
import os
import logging
import numpy as np

from typing import List
from astropy.table import Table


def select_and_save(
        objtype: str,
        savepath: str,
        overwrite: bool=True,
        nobj: int=100_000,
        cols: List[str]=['Z', 'Z_ERR']
) -> None:
    assert objtype in ('QSO', 'STAR', 'GALAXY')
    objtype = '{:<6}'.format(objtype)

    if not os.path.exists(savepath):
        os.makedirs(savepath)
    
    logging.info('Loading data..')
    
    data = Table.read('./res/data/specObj-dr9.fits', format='fits')

    logging.info('Selecting objects..')
    keepcols = ['OBJID', 'PLUG_RA', 'PLUG_DEC', 'CLASS']
    keepcols.extend(cols)
    keepobj = np.where(data["CLASS"] == objtype)
    data = data[keepcols][keepobj]

    del keepobj, keepcols

    N = len(data)
    indxs = np.sort(np.random.choice(N, size=nobj, replace=False))
    
    logging.info(f'Saving {nobj} randomly chosen objects..')
    data[indxs].write(savepath + objtype.strip() + '.fits', format='fits', overwrite=overwrite)

    logging.info(f'{objtype} file is saved.')

