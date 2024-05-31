## Bulk imaging data downloads

A small application for downloading a large number of UGRIZ images (SDSS catalog) of Galaxies, Stars and Quasar objects.

Later, we will add image-to-dataset transformation for training ML models.

### Getting set up

1. Download SDSS scpectroscopic data. In project directiry open terminal and run:

    ```shell
     mkdir ./data
     rsync -lv rsync://dtn.sdss.org/dr9/sdss/spectro/redux/specObj-dr9.fits ./data 
     ```

2. Check jobs.sh. Test code by running 

    ```shell
    python3 main.py routine='test' objects='QSO'
    ```

**Alternatively**, you can run following command
```shell
sh jobs.sh
```
Check, if there is any .npz files in `./data/test/QSO`

### Usage

Set the parameters for images size in degrees, output dimension in pixels, number of objects to download, then run:

```shell
python3 main.py routine='run' objects='QSO'
```
