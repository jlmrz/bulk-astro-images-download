import os
import logging
import numpy as np

from numpy import ndarray 
from tqdm import tqdm
from typing import Tuple, Any
from pathlib import Path

from astropy import units as u
from astropy.coordinates import Longitude, Latitude
from astropy.table import Table
from astroquery.hips2fits import hips2fits

from src.utils import Dictionary

HIPS_CATALOGS = [
    'CDS/P/SDSS9/u',
    'CDS/P/SDSS9/g',
    'CDS/P/SDSS9/r',
    'CDS/P/SDSS9/i',
    'CDS/P/SDSS9/z'
]


def download_image(ra, dec, config: Dictionary[str, Any]) -> ndarray:
    """
    config includes width, height, fov
    """
    img = np.zeros((5, config.width, config.height))

    for n, frame in enumerate(HIPS_CATALOGS):
        img[n] = hips2fits.query(
            hips=frame,
            ra=Longitude(ra * u.deg),
            dec=Latitude(dec * u.deg),
            **config
        )[0].data

    return img


def process_object(objinfo: Tuple, config: Dictionary[str, Any], savepath: Path) -> int:
    """
    Arguments:
        objinfo: Tuple[ra, dec, objtype, z, zerr]
        config: Dictionary with image parameters (heigt x width, angle)
    Returns:
        Status: 1 is success else 0
    """
    ra, dec, objtype, z, zerr = objinfo

    save_fname = '_'.join([objtype, '%.5f_%.5f' % (ra, dec)])

    if not os.path.isfile(savepath / f'{save_fname}.npz'):
        try:
            img = download_image(ra, dec, config)
            np.savez_compressed(
                savepath / save_fname, img=img, redshift=z, zerr=zerr
            )
            return 1

        except ConnectionError as e:
            logging.error(f'Connection error when downloading image: {e}')
            return 0
    else:
        logging.info(f'File {save_fname} already exists.')
        return 0
    

def load_images(config: Dictionary[str, Any], objtype: str, path: Path) -> None:

    data = Table.read(path.parent / f'{objtype}.fits', format='fits')

    success_counter = 0
    for row in tqdm(data.iterrows()):
        success_counter += process_object(row, config, path)

    return success_counter
