mkdir ./data
rsync -lv rsync://dtn.sdss.org/dr9/sdss/spectro/redux/specObj-dr9.fits ./data 
python3 main.py routine='test' objects='QSO'
