
import os, sys

import numpy as np
import glob
import datetime
import pandas as pd



idir = os.path.abspath('/local/AIX/tristan.harmel/project/acix/matchup/data')

sensors=['S2','Landsat']
sensor=sensors[1]
files = glob.glob(idir+'/matchup*'+sensor+'*acixii.csv')
df_tot = pd.DataFrame()
for file in files:

    # if file empty continue
    if os.stat(file).st_size == 0:
        continue
    print(file)

    #read and format
    df = pd.read_csv(file, header=[0, 1, 2], index_col=0, parse_dates=True)
    #df.columns.set_levels(pd.to_numeric(df.columns.levels[2], errors='coerce').fillna(''), level=2, inplace=True)
    df.columns = pd.MultiIndex.from_tuples([(x[0], x[1], pd.to_numeric(x[2], errors='coerce')) for x in df.columns])
    df.sort_index(axis=1, level=2, sort_remaining=False, inplace=True)


    df_tot = df_tot.join(df)


    dff = df.droplevel(0, axis=1).stack()

    # Extract sat and in situ concomitant data
    Rrs_sat = dff.loc[:, (['Rrs_mean'])].dropna()
    Rrs_sat.reset_index(level=0,inplace=True)
    Rrs_sat.index.name='wl'
    #Rrs_sat.level_1.fillna(0,inplace=True)

    Rrs_insitu = dff.loc[:, (['Lwn'])].dropna()
    Rrs_insitu.reset_index(level=0,inplace=True)
    Rrs_insitu.index.name='wl'
    Rrs_insitu=Rrs_insitu.reset_index().dropna().set_index('wl')
    #Rrs_insitu.level_1.fillna(0,inplace=True)

    # merge on nearest wavelength
    match_df = pd.merge_asof(Rrs_sat.sort_index() , Rrs_insitu.sort_index(), left_index=True,right_index=True, by='time', tolerance=20, direction='nearest')
    match_df = match_df.reset_index().set_index(['time','wl']).sort_index()

    print(df.shape)
    df
    dff=pd.concat([dff,df])
