import numpy as np
import os
import logging 
from src.dataloader.select_objects import select_and_save
from src.dataloader.loader import load_images
from src.utils import Dictionary
from astropy.coordinates import Angle
from astropy import units as u

logging.basicConfig(level=logging.INFO)

DATA_DIR = './res/data/'
np.random.seed(seed=0)


def main_test():

    config = Dictionary({
        'width': 16,
        'height': 16,
        'fov': Angle(0.002 * u.deg),
        'projection': 'TSC',
        'min_cut': 0.5,
        'get_query_payload': False,
        'max_cut': 99.5,
    })

    for obj in ('GALAXY', 'QSO', 'STAR'):
        if not os.path.exists(DATA_DIR + 'test/' + obj + '.fits'):
            select_and_save(
                objtype=obj, 
                savepath=DATA_DIR + 'test/',
                nobj=10
            )

        load_images(
            config=config, objtype=obj, path=DATA_DIR + 'test/'
        )
    

if __name__ == '__main__':
    main_test()
