import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as c
from matplotlib.backends.backend_pdf import PdfPages

from mpl_toolkits.basemap import Basemap, shiftgrid
import datetime
import dask
import toolz
import cartopy.crs as ccrs
import xarray as xr
import shapely
from shapely.wkt import dumps, loads
import rasterio
import regionmask

from rasterio.mask import mask

from satmatchup import utils as u

site = "LISCO"
lon, lat = -73.341767, 40.954517
files = '/DATA/Satellite/SENTINEL2/acix/*' + site + '*.nc'
ofile = '/DATA/projet/ACIXII/matchup/matchup_'+site+'_acixii.csv'

# load image data
ds = xr.open_mfdataset(files, concat_dim='time', preprocess=u.get_time)
ds = ds.dropna('time', how='all')

# set ROI mask
shape = loads(u.wktbox(lon, lat, width=100, height=100))
umask = regionmask.Regions_cls('roi_mask', [0], ['roi matchup'], ['roi'], [shape])
roi = umask.mask(ds.coords)
ds['roi'] = roi

ds.where(roi == 0)['Rrs_B2'].isel().plot(x='lon', y='lat', col='time', col_wrap=4, robust=True)

print(ds['Rrs_B2'])
vmax = round(ds['Rrs_B2'].to_dataframe().median()[-1] * 3, 4)
u.plot()._plot_image(ds['Rrs_B2'], vmax=vmax, title=site, filename='test' + site + '.png')

data = ds['Rrs_B2']

fig, (ax, cax) = plt.subplots(nrows=2, figsize=(15, 35),
                              gridspec_kw={"height_ratios": [1, 0.05]})
p = data.isel().plot(x='lon', y='lat', col='time', col_wrap=4, robust=True, size=10, cmap='viridis',
                     cbar_kwargs=dict(orientation='horizontal', pad=.1, aspect=40, shrink=0.6))
for i, ax in enumerate(p.axes.flat):
    if i >= data.time.shape[0]:
        break
    ax.set_title(pd.to_datetime(data.time[i].values))
p.cbar
p.fig.set_size_inches(15, 40)
p.fig.suptitle(site)
p.fig.subplots_adjust(bottom=0.1, top=0.9, left=0.08, right=0.92, wspace=0.02, hspace=0.2)
p.fig.savefig('test' + site + '.png')

# -------------------------
# apply mask from wkt
ds_roi = ds.where(roi == 0)

# -------------------------
# compute statistics over the ROI along time
vars = ['Rrs_B1', 'Rrs_B2', 'Rrs_B3', 'Rrs_B4', 'Rrs_B5', 'Rrs_B6', 'Rrs_B7', 'Rrs_B8', 'Rrs_B8A']
roi_df = ds_roi[vars].to_dataframe().drop(['lat', 'lon'], axis=1)
matchup = roi_df.groupby('time').describe()
# matchup.to_csv(ofile)
matchup.iloc[:, [1, 9, 17, 25, 33]].plot(marker='o')
#
# with PdfPages('multipage_pdf.pdf') as pdf:
#     time = range(12)
#     p = b2.isel().plot(x='lon', y='lat', col='time', col_wrap=10, robust=True, size=10)
#
#     p.fig.savefig(p.fig, bbox_inches='tight')
#
# tmp = ds[['lat', 'lon', 'Rrs_g_B2', 'Rrs_B2']].to_dataframe()
#
# b2.isel(x=10, y=[10, 20]).plot()
# b2.isel(x=10, y=[10, 20]).plot.line(x='time', marker='o')
