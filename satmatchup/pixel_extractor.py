import os, sys
os.environ['HDF5_USE_FILE_LOCKING']='FALSE'
import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import pandas as pd
import xarray as xr
# load image data to debug strange failure of xr.open_mfdataset on mistraou
file = '/nfs/DP/S2/L2/GRS/acix/netcdf/S2A_MSIl2grs_20160309T155132_N0201_R011_T18TXL_20160309T155127_LISCO_GRS.nc'
d = xr.open_dataset(file)

# from mpl_toolkits.basemap import Basemap, shiftgrid
import glob
import datetime
import dask
import toolz
import cartopy.crs as ccrs

import shapely
from shapely.wkt import dumps, loads

import regionmask
import matplotlib.pyplot as plt
# from matplotlib import colors as c
# from matplotlib.backends.backend_pdf import PdfPages
import cmocean as cm
from satmatchup import utils as u

sensors=['S2','Landsat']
sensor=sensors[1]
mistraou = True
overwrite = False
write = True
plot = False #True
# set time tolerance to combine insitu and sat data
tolerance=pd.Timedelta('2h')

if mistraou:
    if 'S2' in sensor:
        satdir = '/nfs/DP/S2/L2/GRS/acix/netcdf/'
    else:
        satdir = '/nfs/DP/Landsat/L2/GRS/acix/netcdf/'
    aeronetdir = '/nfs/DD/aeronet/OCv3/'
    odir = '/local/AIX/tristan.harmel/project/acix/matchup/data'
    figdir = '/local/AIX/tristan.harmel/project/acix/matchup/fig'
else:
    satdir = '/DATA/Satellite/SENTINEL2/acix/'
    aeronetdir = '/DATA/AERONET/OCv3/'
    odir = '/DATA/projet/ACIXII/matchup/'
    figdir = '/DATA/projet/ACIXII/matchup/'
if 'S2' in sensor:
    vars = ['Rrs_B1', 'Rrs_B2', 'Rrs_B3', 'Rrs_B4', 'Rrs_B5', 'Rrs_B6', 'Rrs_B7', 'Rrs_B8', 'Rrs_B8A']
    wl = [442, 492, 559, 664, 704, 740, 782, 832, 864]
    # TODO convert uint8 flags into bin array to select mask
    # flags = ['mask_nodata_mask', 'mask_negative_mask', 'mask_ndwi_mask', 'mask_ndwi_corr_mask', 'mask_high_nir_mask']
else:
    vars = ['Rrs_coastal_aerosol', 'Rrs_blue', 'Rrs_green', 'Rrs_panchromatic', 'Rrs_red', 'Rrs_near_infrared']
    wl = [443, 483, 561, 592, 655, 865]

info = pd.read_csv('aeronet/aeronet_oc_locations_v3.csv')

cmap = cm.tools.crop_by_percent(cm.cm.rain_r,25,which='both')

for idx, row in info.iterrows():
    if idx < 0:
        continue
    site, lon, lat, alt = row.values

    files = glob.glob(satdir + '/*' + site + '*.nc')

    if files.__len__() == 0:
        print('no satellite data available for site ' + site)
        continue

    # set aeronet file
    aeronet_file = aeronetdir + site + '_OCv3.lev15'

    # check if different tiles exist for a given site
    if 'S2' in sensor:
        tiles = np.unique([os.path.basename(f).split('_')[5] for f in files])
    else:
        tiles = np.unique([os.path.basename(f)[3:9] for f in files])

    if tiles.__len__()==1:
        tiles=(tiles)
    for tile in tiles:
        print(tile)
        _files = [item for i,item in enumerate(files) if tile in item]

        # set output file (figures and data)
        ofile = os.path.join(odir, 'matchup_' + site + '_' + sensor+'_'+tile + '_acixii.csv')
        ofig = os.path.join(figdir, 'images_' + site + '_' + sensor+'_'+tile + '_acixii.png')

        if (not(overwrite)) & os.path.exists(ofile):
            continue

        # load image data
        print(' loading images for ' + site)
        #check dims:
        xdim = xr.open_mfdataset(_files[0]).dims.get('x')
        print('xdim: ',xdim)
        _f=[]
        for f in _files:
            d = xr.open_mfdataset(f)
            print(f,'xdim: ',d.dims.get('x'))
            #remove empty arrays
            if (d.SZA.values==0).all():
                continue
            if d.dims.get('x') == xdim:
                _f.append(f)
        if _f == []:
            with open(ofile, 'w'):
                pass
            continue
        print('number of images: ',len(_f))
        ds = xr.open_mfdataset(_f, concat_dim='time', preprocess=u.get_time, mask_and_scale=True, engine='netcdf4')
        ds = ds.reindex(time=sorted(ds.time.values))
        print('processing site ' + site)
        ds = ds.dropna('time', how='all')

        # set ROI mask
        shape = loads(u.wktbox(lon, lat, width=100, height=100))
        exclude = loads(u.wktbox(lon, lat, width=30, height=30))
        print('masking')
        umask = regionmask.Regions_cls('roi_mask', [0, 1], ['roi matchup', 'exclude'], ['roi', 'excl'], [shape, exclude])
        roi = umask.mask(ds.coords)
        ds['roi'] = roi

        # -------------------------
        # apply mask from wkt (subset)
        ds_roi = ds.where(roi == 0)

        # -------------------------
        # apply Quality flag mask
        ds_roi = ds_roi.where(ds_roi.flags == 0)
        # plt.figure()
        # ds_roi['Rrs_B2'].isel(time=0).plot(x='lon', y='lat', robust=True)
        # ds_roi['Rrs_B2'].isel().plot(x='lon', y='lat', col='time', col_wrap=4, robust=True, size=10, cmap='viridis',
        #                      cbar_kwargs=dict(orientation='horizontal', pad=.1, aspect=40, shrink=0.6))
        #
        # print(ds['Rrs_B2'])
        # -------------------------
        # compute statistics over the ROI along time
        roi_df = ds_roi[vars].to_dataframe().drop(['lat', 'lon'], axis=1)
        matchup = roi_df.groupby('time').describe()

        matchup = u.data().format_df(matchup, vars, wl)
        # if write:
        #     matchup.to_csv(ofile)

        # -------------------------
        # Plotting section
        # vmax = round(ds['Rrs_B2'].to_dataframe().median()[-1] * 3, 4)
        # u.plot()._plot_image(ds['Rrs_B2'], vmax=vmax, title=site, filename='test' + site + '.png')
        if plot:
            print('plotting...')
            data = ds[vars[2]]
            # data= ds['flags']
            # data= ds_roi['Rrs_B2']
            p = u.plot().plot_wrap(data, ofig, site,cmap=cmap)
            # matchup.iloc[:, [1, 9, 17, 25, 33]].plot(marker='o')
            plt.close()

        # -------------------------
        # Merge with in situ data

        print('merging with in situ data...')
        try:
            aeronet_df = u.data().read_aeronet_ocv3(aeronet_file)
            aeronet_matchup = pd.merge_asof(matchup, aeronet_df, left_index=True, right_index=True,
                                            direction='nearest', tolerance=tolerance)
            aeronet_matchup.to_csv(ofile)
        except:
            print('no aeronet data available')
