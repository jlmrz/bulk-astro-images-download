import os
import hydra
import logging

from pathlib import Path
from omegaconf import DictConfig, OmegaConf

from src.dataloader.select_objects import select_and_save
from src.dataloader.loader import load_images_csv, load_images_fits, npz_to_hdf5
from src.utils import Dictionary
from astropy.coordinates import Angle
from astropy import units as u


@hydra.main(version_base=None, config_path="config", config_name="main")
def main(cfg: DictConfig):
    routine, obj, source = cfg.routine, cfg.objects, cfg.data_source

    assert obj in ('QSO', 'STAR', 'GALAXY') or routine in ('test', 'run')
    assert source in ('csv', 'fits')

    load_images = load_images_csv if source == 'csv' else load_images_fits
    num_objects = 10 if routine == 'test' else cfg.number_of_objects

    images_config = Dictionary(OmegaConf.to_container(cfg.images_config))
    images_config.fov = Angle(images_config.fov * u.deg)

    data_dir = Path(cfg.directories.data_run)
    results_obj_dir = Path(cfg.directories.results)

    if not os.path.exists(results_obj_dir):
        results_obj_dir.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(cfg.data_file) or cfg.overwrite:
        logging.info(f"Selecting and saving objects at {data_dir}")
        
        select_and_save(
            objtype=obj, savepath=data_dir, nobj=num_objects, source=source
        )

    logging.info(f"Loading images" )

    if routine != 'run':
        success_counter = load_images(
            config=images_config, objtype=obj, path=results_obj_dir
        )

        logging.info(f'Number of objects processed: {success_counter}')

    logging.info(f'Creating hdf5 file..')

    npz_to_hdf5(
        img_dir=results_obj_dir
    )



if __name__ == '__main__':    
    os.environ["HYDRA_FULL_ERROR"] = "1" 
    logging.basicConfig(level=logging.INFO)

    main()
