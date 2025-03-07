# -*- coding: utf-8 -*-
"""Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10ElOBc35FZrUOBE4848sTyL3_l6TqerL

# **RESAMPLING dan COMPOSITE**

Link drive data Himawari : https://drive.google.com/drive/folders/1oYB7ovRjUQqY9hp3U46OuEHOgWZGPjNj?usp=sharing
"""

import sys
from google.colab import drive
drive.mount('/content/drive')

"""Set up folder instalasi `SatPy` di Google Drive"""

sys.path.insert(0,'/content/drive/MyDrive/metsat_libs/')

"""Atau install library yang dibutuhkan di sesi ini saja:"""

!pip install satpy pyyaml==5.4.1 cartopy rasterio

"""(Optional) Buat link folder (https://bit.ly/CartopyData) ke google drive anda lalu tambahkan ke konfigurasi cartopy. Langkah ini dilakukan agar anda tidak perlu men-download fitur peta (coastline, borders, etc) saat menggambar (dan mengatasi server Natural Earth yang terkadang down)"""

import cartopy
cartopy.config['data_dir']='/content/drive/MyDrive/cartopy/'

"""# Resampling"""

from dask.diagnostics import ProgressBar
from satpy import Scene, find_files_and_readers
from datetime import datetime

indir='drive/MyDrive/KULIAH/PRAKTIKUM/METSAT/MODUL 1/Metsat/'
files = find_files_and_readers(start_time=datetime(2021, 9, 30, 7, 0),
                               end_time=datetime(2021, 9, 30, 7, 10),
                               base_dir=indir,
                               reader='ahi_hsd')

scn = Scene(reader='ahi_hsd', filenames=files)
#Scene menyimpan semua informasi yang ada

"""Check available channels:"""

scn.available_dataset_names()

"""Load all the channels:"""

scn.load(['B01','B02','B03'])

"""Check the `area` attributes"""

scn['B01'].attrs['area']
#Cari informasi yang ada
#Data dari geostationer jadi proyeksi geos

scn['B02'].attrs['area']

scn['B03'].attrs['area']

"""Notice the difference in size (rows and columns) between the two area definitions, the small difference in extents, but also how the projection parameters are exactly the same. This is because these channels are on the same projection (coordinate system), but their individual pixels are different **resolutions**. Each of channel `B01`and `B02` pixels represents 1 kilometer on the geostationary projection, while each of channel `B03` pixels represents 0.5 kilometers."""

# B01 and B02 ressolution (in meters)
(5500000.0355+5500000.0355)/11000

# B03 ressolution (in meters)
(5499999.9684+5499999.9684)/22000

new_scn = scn.resample(resampler='native') #Tujuan Resampling utk menyamakan resolusi
new_scn['B01'].shape == new_scn['B03'].shape #is the channels now have same resolution?

new_scn['B01'].attrs['area']

"""The resample method has given a new `Scene` object with every DataArray we had before, but resampled to the same area or region. By default, it used the highest resolution `AreaDefinition` of the input data (`scn.max_area()`). In this case that's the 0.5km area from `B03`. If we look at the area of `B01` now we can see it is also at 0.5km."""

comb = new_scn['B01'] + new_scn['B02'] + new_scn['B03']  #COMPOSITE
comb

"""## Dynamic Areas

"""

from pyresample import create_area_def
create_area_def?

""" We can use the `create_area_def` function to create a `DynamicAreaDefinition` if needed. Let's make a dynamic area where we know the projection and the resolution we want for each pixel (0.1 degree)."""

my_dynamic_area = create_area_def('indonesia', {'proj': 'merc', 'lon_0': 140.7},
                                  resolution=0.1,units='degrees',area_extent=[90,-15,130,15])
my_dynamic_area

"""Resample the datasets:"""

dynamic_scn = scn.resample(my_dynamic_area)

"""Check the `area` attributes:"""

dynamic_scn['B01'].attrs['area']

dynamic_scn['B03'].attrs['area']

"""Pay attention to the number of pixels for each channel. Because we resample all the channel to 0.1 degree resolution, all channel will have the same number of pixels.

 Now, we can write the dataset to disk as simple image (png):
"""

imdir='/content/drive/MyDrive/KULIAH/PRAKTIKUM/METSAT/MODUL 1/OUTPUT'
with ProgressBar():
  dynamic_scn.save_datasets(base_dir=imdir,writer='simple_image',filename='resample_01deg_{name}_{start_time:%Y%m%d_%H%M%S}.png')
  #Simple image itu png

"""## Cropping and Aggregating"""

crop_scn = scn.crop(ll_bbox=[90, -15, 130, 15])

"""Check again the area attributes:"""

crop_scn['B01'].attrs['area']

crop_scn['B03'].attrs['area']

"""Notice that the number of pixels are different between channels, because no resmpling has be done."""

with ProgressBar():
  crop_scn.save_datasets(base_dir=imdir,writer='simple_image',filename='crop_{name}_{start_time:%Y%m%d_%H%M%S}.png')

agg_scn = scn.aggregate(y=10, x=10)

agg_scn['B01'].attrs['area']

agg_scn['B03'].attrs['area']

with ProgressBar():
  agg_scn.save_datasets(base_dir=imdir,writer='simple_image',filename='agg_ave_{name}_{start_time:%Y%m%d_%H%M%S}.png')

agg_scn2 = scn.aggregate(y=10, x=10, func='max')
#KALAU MAU FULL DAYS PAKAI AGGREGATE

with ProgressBar():
  agg_scn2.save_datasets(base_dir=imdir,writer='simple_image',filename='agg_max_{name}_{start_time:%Y%m%d_%H%M%S}.png')

"""We've now finished learning about the `resample`, `crop`, and `aggregate` methods for taking data as provided and manipulating it to be the resolution, size, and region that we wish to analyze.

# RGBs and Other Composites
"""

from IPython.display import IFrame, display
filepath = "https://www.data.jma.go.jp/mscweb/technotes/msctechrep65-1.pdf" #Buka aja manual copas
IFrame(filepath, width=1200, height=400)
#Pakai composite utk impresentasi warnanya

scn.available_composite_names()

scn.load(['true_color_raw'])

'true_color_raw' in scn

new_scn = scn.resample(scn.min_area(), resampler='native')
new_scn['true_color_raw']
#min_area() mengubah ke resolusi terendah

new_scn['true_color_raw'].coords['bands']

"""Let's save this product to a PNG image to
get an idea of what an `True Color` RGB looks like.
"""

with ProgressBar():
  new_scn.save_datasets(base_dir=imdir,writer='simple_image',filename='{name}_{start_time:%Y%m%d_%H%M%S}.png')

scn_lores=new_scn.aggregate(y=10, x=10) #10 berarti dalam 10 menit waktunya

"""Let's plot our `True Color` RGB composite."""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt
from satpy.writers import get_enhanced_image

plt.figure()
img = get_enhanced_image(scn_lores['true_color_raw'])
# get DataArray out of `XRImage` object
img_data = img.data
img_data.plot.imshow(rgb='bands', vmin=0, vmax=1)
plt.savefig('drive/My Drive/KULIAH/PRAKTIKUM/METSAT/MODUL 1/OUTPUT/PLOT-TrueColorRGB composite.png')

