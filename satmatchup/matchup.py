
import os, sys

import numpy as np
import glob
import datetime
import pandas as pd
import re
from satmatchup import utils as u

irr = u.irradiance()
irr.load_F0()

idir = os.path.abspath('/local/AIX/tristan.harmel/project/acix/matchup/data')
idir = os.path.abspath('/DATA/projet/ACIXII/matchup/data')

sensors=['S2','Landsat']
sensor=sensors[1]
files = glob.glob(idir+'/matchup*'+sensor+'*acixii.csv')
df_tot = pd.DataFrame()

for file in files:

    # if file empty continue
    if os.stat(file).st_size == 0:
        continue
    print(file)
    site = re.sub(r'.*matchup_','',file)
    site = re.sub(r'_'+sensor+'.*','',site)
    print(site)

    #read and format
    df = pd.read_csv(file, header=[0, 1, 2], index_col=0, parse_dates=True)
    #df.columns.set_levels(pd.to_numeric(df.columns.levels[2], errors='coerce').fillna(''), level=2, inplace=True)
    df.columns = pd.MultiIndex.from_tuples([(x[0], x[1], pd.to_numeric(x[2], errors='coerce')) for x in df.columns])
    df.sort_index(axis=1, level=2, sort_remaining=False, inplace=True)


    #df_tot = df_tot.join(df)


    dff = df.droplevel(0, axis=1).stack()

    # Extract sat and in situ concomitant data
    Rrs_sat = dff.loc[:, (['Rrs_mean'])].dropna()
    Rrs_sat.reset_index(level=0,inplace=True)
    Rrs_sat.index.name='wl'
    #Rrs_sat.level_1.fillna(0,inplace=True)

    Rrs_insitu = dff.loc[:, (['Lwn'])].dropna()
    # convert Lwn to Rrs
    Rrs_insitu['Rrs'] = Rrs_insitu.Lwn.values / (irr.get_F0(Rrs_insitu.index.get_level_values(1))*0.1)
    Rrs_insitu.drop(['Lwn'],axis=1,inplace=True)
    Rrs_insitu.reset_index(level=0,inplace=True)
    Rrs_insitu.index.name='wl'
    Rrs_insitu=Rrs_insitu.reset_index().dropna().set_index('wl')
    #Rrs_insitu.level_1.fillna(0,inplace=True)

    if (Rrs_insitu.__len__() == 0) | (Rrs_sat.__len__() == 0):
        continue

    # merge on nearest wavelength
    match_df = pd.merge_asof(Rrs_sat.sort_index() , Rrs_insitu.sort_index(), left_index=True,right_index=True, by='time', tolerance=20, direction='nearest')
    match_df['site']=site
    match_df = match_df.reset_index().set_index(['time','wl','site']).sort_index()
    df_tot = pd.concat([df_tot,match_df])


df_tot.plot.scatter(x='Rrs_mean',y='Rrs',c=df_tot.index.get_level_values(1))
df_tot.hist(by='site', bins=15, stacked=True, alpha=0.5)
df_tot.hist(by='wl', bins=25, stacked=True, alpha=0.5, density=1)


df_tot.groupby('wl').describe()