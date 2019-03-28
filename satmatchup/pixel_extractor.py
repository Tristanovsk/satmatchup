import os, sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
# from matplotlib import colors as c
# from matplotlib.backends.backend_pdf import PdfPages

#from mpl_toolkits.basemap import Basemap, shiftgrid
import datetime
import dask
import toolz
import cartopy.crs as ccrs
import xarray as xr
import shapely
from shapely.wkt import dumps, loads

import regionmask

from satmatchup import utils as u

mistraou=True
write=True


if mistraou:
    satdir = '/nfs/DP/S2/L2/GRS/acix/netcdf/'
    aeronetdir = '/nfs/DD/aeronet/OCv3/'
    odir = '/local/AIX/tristan.harmel/project/acix/matchup/data'
    figdir = '/local/AIX/tristan.harmel/project/acix/matchup/fig'
else:
    satdir = '/DATA/Satellite/SENTINEL2/acix/'
    aeronetdir = '/DATA/AERONET/OCv3/'
    odir = '/DATA/projet/ACIXII/matchup/'
    figdir ='/DATA/projet/ACIXII/matchup/'



site = "LISCO"
lon, lat = -73.341767, 40.954517

info = pd.read_csv('aeronet/aeronet_oc_locations_v3.csv')
site,lon, lat,alt = info.iloc[1,].values
for idx,row in info.iterrows():
    site,lon, lat,alt = row.values

files = satdir+'/*' + site + '*.nc'
aeronet_file = aeronetdir + site + '_OCv3.lev20'
ofile = os.path.join(odir,'matchup_'+site+'_acixii.csv')
ofig = os.path.join(figdir,'images_' + site + '.png')


# load image data

ds = xr.open_mfdataset(files, concat_dim='time', preprocess=u.get_time, mask_and_scale=True)
ds = ds.dropna('time', how='all')

# set ROI mask
shape = loads(u.wktbox(lon, lat, width=100, height=100))
exclude = loads(u.wktbox(lon, lat, width=30, height=30))
#shape = shape.difference(exclude) #shapely.geometry.Polygon(shape,[exclude])
# TODO exclude platform area from roi mask
#donut = shapely.geometry.Polygon(shape,[exclude])

umask = regionmask.Regions_cls('roi_mask', [0,1], ['roi matchup','exclude'], ['roi','excl'], [shape,exclude])

roi = umask.mask(ds.coords)
roi.plot()
ds['roi'] = roi
ds['flags'].isel(time=0).plot(x='lon', y='lat', robust=True)


vars = ['Rrs_B1', 'Rrs_B2', 'Rrs_B3', 'Rrs_B4', 'Rrs_B5', 'Rrs_B6', 'Rrs_B7', 'Rrs_B8', 'Rrs_B8A']
wl = [442, 492, 559, 664, 704, 740, 782, 832, 864]
# TODO convert uint8 flags into bin array to select mask
#flags = ['mask_nodata_mask', 'mask_negative_mask', 'mask_ndwi_mask', 'mask_ndwi_corr_mask', 'mask_high_nir_mask']

# -------------------------
# apply mask from wkt (subset)
ds_roi = ds.where(roi == 0)

# -------------------------
# apply Quality flag mask
ds_roi = ds_roi.where(ds_roi.flags==0)
plt.figure()
ds_roi['Rrs_B2'].isel(time=0).plot(x='lon', y='lat', robust=True)
ds_roi['Rrs_B2'].isel().plot(x='lon', y='lat', col='time', col_wrap=4, robust=True, size=10, cmap='viridis',
                     cbar_kwargs=dict(orientation='horizontal', pad=.1, aspect=40, shrink=0.6))

print(ds['Rrs_B2'])
# -------------------------
# compute statistics over the ROI along time
roi_df = ds_roi[vars].to_dataframe().drop(['lat', 'lon'], axis=1)
matchup = roi_df.groupby('time').describe()

matchup.iloc[:, [1, 9, 17, 25, 33]].plot(marker='o')

h1 = matchup.columns.get_level_values(0)+'_'+ matchup.columns.get_level_values(1)
h2 = matchup.columns.get_level_values(0).str.replace('_.*','')+'_'+ matchup.columns.get_level_values(1)
h3 = matchup.columns.get_level_values(0)
for band,num in reversed(list(zip(vars,wl))):
    h3=h3.str.replace(band,str(num))
h3 = pd.to_numeric(h3, errors='coerce')

tuples = list(zip(h1, h2, h3))
matchup.columns = pd.MultiIndex.from_tuples(tuples, names=['l0', 'l1', 'l2'])
if write:
    matchup.to_csv(ofile)

aeronet_df = u.data().read_aeronet_ocv3(aeronet_file)

aeronet_matchup = pd.merge_asof(matchup,aeronet_df,left_index=True, right_index=True,tolerance=pd.Timedelta('2h'))
aeronet_matchup.to_csv(ofile)

# -------------------------
# Plotting section
# vmax = round(ds['Rrs_B2'].to_dataframe().median()[-1] * 3, 4)
# u.plot()._plot_image(ds['Rrs_B2'], vmax=vmax, title=site, filename='test' + site + '.png')

data = ds['Rrs_B2']
data= ds['flags']
data= ds_roi['Rrs_B2']
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
p.fig.savefig(ofig)