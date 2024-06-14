import os
import logging
import time
import h5py

import numpy as np
import pandas as pd

from numpy import ndarray 
from tqdm import tqdm
from typing import Any
from pathlib import Path

from astropy import units as u
from astropy.coordinates import Longitude, Latitude
from astropy.table import Table
from astroquery.hips2fits import hips2fits

from http.client import RemoteDisconnected
from requests.exceptions import JSONDecodeError, ConnectionError

from src.utils import Dictionary


HIPS_CATALOGS = [
    'CDS/P/SDSS9/u',
    'CDS/P/SDSS9/g',
    'CDS/P/SDSS9/r',
    'CDS/P/SDSS9/i',
    'CDS/P/SDSS9/z'
]


class AstroObject:
    def __init__(
            self,
            objtype: str, objid: int,
            ra: float, dec: float,
            z: float, zerr: float
) -> None:
        self.objtype = objtype
        self.objid = objid
        self.ra = ra
        self.dec = dec
        self.z = z
        self.zerr = zerr

        try:
            self.name = str(int(objid))
        except TypeError:
            self.name = '%.5f_%.5f' % (ra, dec)
    
    def process_object(self, config: Dictionary[str, Any], savepath: str) -> int:
        """
        Returns:
            Status: 1 is success else 0
        """
        save_fname = '_'.join([self.objtype, self.name])

        if not os.path.isfile(savepath / f'{save_fname}.npz'):
            img = self._download_img(config)
            if img.all():
                np.savez_compressed(
                    savepath / save_fname, img=img, redshift=self.z, zerr=self.zerr
                )
                return 1 
            else:
                logging.info('Nothing to be saved.')
                return 0
        else:
            logging.info(f'File {save_fname} already exists.')
            return 0

    def _download_img(self, config: Dictionary[str, Any]) -> ndarray:
        """For some objects hips2fits has internal failures. It leads to non-obvious exception handling below."""

        img = np.zeros((5, config.width, config.height))

        for n, frame in enumerate(HIPS_CATALOGS):
            try:
                img[n] = hips2fits.query(
                    hips=frame,
                    ra=Longitude(self.ra * u.deg),
                    dec=Latitude(self.dec * u.deg),
                    **config
                )[0].data

            except Exception as e:        
                if isinstance(e, JSONDecodeError):
                    logging.info(f'Internal server error occured. Skipping the object {int(self.objid)}.')
                    break

                elif isinstance(e, RemoteDisconnected) or isinstance(e, ConnectionError):
                    logging.info(f'Remote diconnected. Sleeping for a while and then trying again.')
                    time.sleep(3)
                    try:
                        img[n] = hips2fits.query(
                            hips=frame,
                            ra=Longitude(self.ra * u.deg),
                            dec=Latitude(self.dec * u.deg),
                            **config
                        )[0].data

                    except JSONDecodeError:        
                        logging.info(f'Internal server error occured. Skipping the object {int(self.objid)}.')
                        break
                else:
                    raise e
        return img


def _load(row, objtype, config, path):
    obj = AstroObject(objtype, *row)
    return obj.process_object(config, path) 


def load_images_csv(config: Dictionary[str, Any], objtype: str, path: Path) -> int:
    tqdm.pandas()
    data = pd.read_csv(path.parent /  f'{objtype}.csv', index_col=False).drop_duplicates()
    success_counter = data.progress_apply(lambda x: _load(x, objtype, config, path), axis=1)
    return success_counter.sum()

    
def load_images_fits(config: Dictionary[str, Any], objtype: str, path: Path) -> int:

    data = Table.read(path.parent / f'{objtype}.fits', format='fits')

    success_counter = 0
    for row in tqdm(data.iterrows()):
        obj = AstroObject(objtype, *row)
        success_counter += obj.process_object(config, path)

    return success_counter


def npz_to_hdf5(img_dir: Path) -> None:
    with h5py.File(str(img_dir) + '.hdf5', 'w') as hdf5_file:
        img = []
        zerr = []
        z = []
        for file in tqdm(os.listdir(img_dir)):
            data = np.load(img_dir / file)
            img.append(data['img'])
            z.append(data['redshift'].item())
            zerr.append(data['zerr'].item())

        _ = hdf5_file.create_dataset(f'images', data=img)
        _ = hdf5_file.create_dataset(f'redshift', data=z)
        _ = hdf5_file.create_dataset(f'zerr', data=zerr)
