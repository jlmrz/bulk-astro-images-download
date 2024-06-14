
import os
import logging
import numpy as np
import pandas as pd

from pathlib import Path
from astropy.table import Table


def select_and_save(
        objtype: str,
        savepath: Path,
        nobj: int,
        source: str = 'fits'
) -> None:

    if source == 'fits' and not os.path.exists(savepath.parent / 'specObj-dr9.fits'):
        raise FileNotFoundError(
            "Run jobs.sh to download specObj-dr9.fits file from SDSS catalog. " +\
                "For further information see README.md."
            )
    
    if source == 'csv' and not os.path.exists(savepath.parent / f'csv/DR9_{objtype}.csv'):
        raise FileNotFoundError(
            "Download data from SDSS catalog using CasJobs. " +\
                "For further information see README.md."
            )

    logging.info('Loading table data')

    if source == 'csv':
        data = pd.read_csv(savepath.parent / source / f'DR9_{objtype}.csv')
        keepcols = ['objid', 'ra', 'dec', 'redshift', 'redshiftErr']
        data = data[data.redshiftErr < 1e-3]
        savenm = f'{objtype}.csv'
    else:
        data = Table.read(savepath.parent / 'specObj-dr9.fits', format='fits')
        keepobj = np.where((data["CLASS"] == '{:<6}'.format(objtype)) & np.all((data["OBJID"] != np.zeros(5)), axis=1))
        keepcols = ['OBJID', 'PLUG_RA', 'PLUG_DEC', 'Z', 'Z_ERR']
        data = data[keepobj]
        savenm = f'{objtype.strip()}.fits'
        
    data = data[keepcols]
    N = len(data)
    nobj = nobj if nobj < N else N
    
    indxs = np.sort(np.random.choice(N, size=nobj, replace=False))
    
    logging.info(f'Saving {nobj} randomly chosen objects..')
    save(data, indxs, source, path=savepath / savenm)
    logging.info(f'{objtype} file is saved.')
 
def save(data, indxs, source, path):
    if source == 'csv':
        data.iloc[indxs].to_csv(path, index=False)
    else:
        data[indxs].write(path, format='fits', overwrite=True)
