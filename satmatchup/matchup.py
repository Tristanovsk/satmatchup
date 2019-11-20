import chart_studio
chart_studio.tools.set_credentials_file(username='tristanovsk', api_key='e2aYFdkLAwuAnCZn8aWe')
import chart_studio.plotly as py
import os, sys
import matplotlib.pyplot as plt
import itertools
import numpy as np
import glob
import datetime
import pandas as pd
import re
from scipy import stats
from satmatchup import utils as u
from satmatchup.metrics import metrics

irr = u.irradiance()
irr.load_F0()

publish = True

idir = os.path.abspath('/local/AIX/tristan.harmel/project/acix/matchup/data')
idir = os.path.abspath('/DATA/projet/ACIXII/matchup_mask/data')
odir = os.path.abspath('/DATA/projet/ACIXII/matchup_mask/fig')
aeronet_params = ["Lw","Lwn","Lwn_f/Q"]
aeronet_param = aeronet_params[1]
sensors = ['S2', 'Landsat']
sensor = sensors[1]
df_tot = pd.DataFrame()
for sensor in sensors:
    files = glob.glob(idir + '/matchup*' + sensor + '*acixii.csv')

    for file in files:

        # if file empty continue
        if os.stat(file).st_size == 0:
            continue
        print(file)
        site = re.sub(r'.*matchup_', '', file)
        site = re.sub(r'_' + sensor + '.*', '', site)
        print(site)

        # read and format
        df = pd.read_csv(file, header=[0, 1, 2], index_col=0, parse_dates=True)
        # df.columns.set_levels(pd.to_numeric(df.columns.levels[2], errors='coerce').fillna(''), level=2, inplace=True)
        df.columns = pd.MultiIndex.from_tuples([(x[0], x[1], pd.to_numeric(x[2], errors='coerce')) for x in df.columns])
        df.sort_index(axis=1, level=2, sort_remaining=False, inplace=True)

        # df_tot = df_tot.join(df)

        dff = df.droplevel(0, axis=1).stack()

        # Extract sat and in situ concomitant data
        dff.loc[dff['Rrs_50%']==0,'Rrs_50%']=np.nan
        Rrs_sat = dff.loc[:, (['Rrs_50%', 'Rrs_std','Rrs_count'])].dropna()

        Rrs_sat.reset_index(level=0, inplace=True)
        Rrs_sat.index.name = 'wl'
        # Rrs_sat.level_1.fillna(0,inplace=True)

        Rrs_insitu = dff.loc[:, ([aeronet_param])].dropna()
        # convert Lwn to Rrs
        Rrs_insitu['Rrs'] = Rrs_insitu[aeronet_param].values / (irr.get_F0(Rrs_insitu.index.get_level_values(1)) * 0.1)
        Rrs_insitu.drop([aeronet_param], axis=1, inplace=True)
        Rrs_insitu.reset_index(level=0, inplace=True)
        Rrs_insitu.index.name = 'wl'
        Rrs_insitu = Rrs_insitu.reset_index().dropna().set_index('wl')
        # Rrs_insitu.level_1.fillna(0,inplace=True)

        if (Rrs_insitu.__len__() == 0) | (Rrs_sat.__len__() == 0):
            continue

        # merge on nearest wavelength
        match_df = pd.merge_asof(Rrs_sat.sort_index(), Rrs_insitu.sort_index(), left_index=True, right_index=True,
                                 by='time', tolerance=20, direction='nearest')
        match_df['site'] = site
        match_df['satellite'] = sensor
        match_df = match_df.reset_index().set_index(['time', 'wl', 'site']).sort_index()

        df_tot = pd.concat([df_tot, match_df])

# rough filtering
#df_tot.groupby(level=0).filter(lambda x: x.loc[(slice(None),864.0),'Rrs_mean']<0.003)

df_tot.plot.scatter(x='Rrs_50%', y='Rrs', c=df_tot.index.get_level_values(1))
df_tot.hist(by='site', bins=15, stacked=True, alpha=0.5)
df_tot.hist(by='wl', bins=25, stacked=True, alpha=0.5, density=1)

df_tot = df_tot.reset_index() #df_tot.reset_index(level=[1,2])
df_tot.dropna(inplace=True)
df_tot["date"] = df_tot.time.dt.date
df_tot.sort_values(by=['wl','site'],inplace=True)
df_tot['AD']=df_tot['Rrs_50%'] - df_tot.Rrs
df_tot['wl_str'] = df_tot.wl.astype('str')
# df_tot['row']=0
# df_tot.loc[df_tot.wl>700,'row']=1



import plotly.express as px
import plotly.offline as po
import plotly.graph_objs as go
import plotly.figure_factory as ff



# define parameters to be formated as decimal (.4f) or percentage (.2f)
params_dec =['rmse', 'rmse_log', 'bias', 'bias_log', 'mae','slope', 'intercept', 'r_value']
params_percent=['mae_log', 'mape']
ncol = 4

def table(stat_df):
    table = go.Table(
    columnwidth=[110,70],
    header=dict(
        #values=list(df.columns[1:]),
        values=stat_df.keys().values,
        font=dict(size=18),
        line = dict(color='rgb(50, 50, 50)'),
        align = ['left','center'],
        height=40,
        #fill = dict(color='#d562be'),
    ),
    cells=dict(
        values=[stat_df[k].tolist() for k in stat_df.columns],
        line = dict(color='rgb(50, 50, 50)'),
        font=dict(size=15),
        align = ['left','center'],
        fill = dict(color=['rgba(255, 127, 14,0.8)', 'rgba(255, 127, 14, 0.23)']),
        height=30
        #fill = dict(color='#f5f5fa')
    )
    )
    return [table]


df_tot.rename(columns={"wl": "Wavelength (nm)"},inplace=True)
publish=False
for sensor in sensors:
    if sensor == 'all':
        dff = df_tot
    else:
        dff = df_tot.loc[df_tot.satellite==sensor]

    #------------------------
    # tables summarizing metrics parameters
    #------------------------
    for by_ in ['site','Wavelength (nm)']:
        stat = metrics(dff.Rrs, dff['Rrs_50%'])
        stat_df = pd.DataFrame.from_records([stat.to_dict()])
        if by_ == 'site':
            stat_df[by_]= 'All sites'
        else:
            stat_df[by_] = 'All wavelengths'
        for key, group in dff.groupby(by=by_):
            print(key)
            stat = metrics(group.Rrs,group['Rrs_50%'])
            stat = pd.DataFrame.from_records([stat.to_dict()])
            stat[by_]=key
            stat_df = pd.concat([stat_df,stat])
        stat_df.set_index(by_,inplace=True)
        stat_df.reset_index(inplace=True)
        stat_df[params_dec]=stat_df[params_dec].applymap(lambda x: '{:,.4f}'.format(x))
        stat_df[params_percent]=stat_df[params_percent].applymap(lambda x: '{:,.2f}'.format(x))
        fig = {"data": table(stat_df), "layout":go.Layout(title=f"AERONET-OC matchup; metrics summary for "+sensor, height=600)}
        if publish:
        #fig=ff.create_table(stat_df,index=True)
            py.plot(fig,filename='acix-ii_grs_aeronet-oc_metrics_table_by_'+by_+'_' + sensor,auto_open=False)
        else:
            po.plot(fig,filename=os.path.join(odir,'acix-ii_grs_aeronet-oc_metrics_table_by_'+by_+'_' + sensor))


    #------------------------
    # error distribution
    #------------------------
    if publish:
        # to be under the upload limit
        dff = dff[dff.site != 'Irbe_Lighthouse']
    fig = ff.create_distplot([group.AD for key, group in dff.groupby(by='site')],
                             [key for key, group in dff.groupby(by='site')], bin_size=.0005)
    fig.update_layout(title='AERONET-OC error distribution (sat - ref)')
    if publish:
         py.plot(fig, filename='acix-ii_grs_aeronet-oc_error_distribution_' + sensor,auto_open=False)
    else:
         po.plot(fig, filename=os.path.join(odir,'acix-ii_grs_aeronet-oc_error_distribution_' + sensor))

    #------------------------
    # interactive plot
    #------------------------
    for by_ in ['site','Wavelength (nm)']:
        fig = px.scatter(dff, x="Rrs", y="Rrs_50%",  color="Wavelength (nm)", hover_name="site", hover_data=['date','satellite','Rrs_count'],
                         trendline="ols", trendline_color_override='red',opacity=0.5,
                         range_x=[-0.005,0.04],range_y=[-0.005,0.04],animation_frame=by_,
                         title="AERONET-OC matchup for "+sensor, error_y="Rrs_std")# ,height =900,width=1200)
        fig.add_trace(
                go.Scatter(
                x=[-1, 4],
                y=[-1, 4],
                mode="lines",
                line=go.scatter.Line(color="black",dash='dot'),
                showlegend=False))


        fig.update_xaxes(showgrid=False)
        fig.update_traces(
             line=dict(dash="dot", width=2),
             selector=dict(type="scatter", mode="lines"))
        fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                          selector=dict(mode='markers'))
        if publish:
            fig.update_layout(title_font_size=24, margin=dict(l=265, r=200, t=100, b=100))
            py.plot(fig, filename='acix-ii_grs_aeronet-oc_matchup_by_'+by_+'_'+sensor,auto_open=False)
        else:
            fig.update_layout(title_font_size=24, margin=dict(l=300, r=20, t=200, b=20))
            po.plot(fig, filename=os.path.join(odir,'acix-ii_grs_aeronet-oc_matchup_by_'+by_+'_'+sensor))

    #------------------------
    # plot by subplot
    #------------------------
    fig = px.scatter(dff, x="Rrs", y="Rrs_50%",  color="Wavelength (nm)", hover_name="site", hover_data=['date','satellite'],
                     facet_col="site", trendline="ols", trendline_color_override='red',opacity=0.5,
                     range_x=[-0.005,0.04],range_y=[-0.005,0.04],animation_group='Wavelength (nm)',
                     title="AERONET-OC matchup for "+sensor, error_y="Rrs_std" ,facet_col_wrap=ncol,height =2100)

    for icol, irow in  itertools.product(range(4),range(len(fig._validate_get_grid_ref()))):
        fig.add_trace(
            go.Scatter(
            x=[-1, 4],
            y=[-1, 4],
            mode="lines",
            line=go.scatter.Line(color="black",dash='dot'),
            showlegend=False),row=irow+1,col=icol+1
        )
       # fig.add_annotation(text='Acceptance: '+str(icol)+'%\nAlpha:'+str(irow),row=irow+1,col=icol+1)

    fig.update_layout(title_font_size=24)
    fig.update_xaxes(showgrid=False)
    fig.update_traces(
         line=dict(dash="dot", width=2),
         selector=dict(type="scatter", mode="lines"))
    fig.update_traces(marker=dict(size=12,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                      selector=dict(mode='markers'))
    fig.show()
    if publish:
        py.plot(fig, filename='acix-ii_grs_aeronet-oc_matchup_subplot_'+sensor,auto_open=False)
    else:
        po.plot(fig, filename=os.path.join(odir,'acix-ii_grs_aeronet-oc_matchup_subplot_'+sensor))


#
#
# x = df_tot.Rrs
# y = df_tot['Rrs_50%']
# mask = ~np.isnan(x) & ~np.isnan(y)
# x=x[mask]
# y=y[mask]
# stats.linregress(x,y)
# slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
# regline = slope*x+intercept
#
# c = df_tot.index.get_level_values(1)
# text = ['<br />'.join(i) for i in zip(df_tot.index.get_level_values(0).map(str), df_tot.index.get_level_values(2))]
#
# ystd = df_tot.Rrs_std
# xstd = ystd * 0
#
# trace = go.Scatter(
#     x=x,
#     y=y,
#     mode='markers',
#     name='measured',
#     error_y=dict(
#         type='data',
#         array=ystd,
#         color='grey',
#         thickness=1.5,
#         width=3,
#     ),
#     error_x=dict(
#         type='data',
#         array=xstd,
#         color='grey',
#         thickness=1.5,
#         width=3,
#     ),
#     marker=dict(
#         color=c,
#         opacity=0.5,
#         colorscale='Rainbow',
#         showscale=True,
#         size=10
#     ),
#
#     text=text
# )
#
# p = go.Scatter(x=x,
#                 y=regline,
#                 mode='lines',
#                 line=dict(color='blue', width=3),
#
#                 )
#
# # format the layout
# layout = go.Layout(
#     autosize=False,
#     width=750,
#     height=750,
#     paper_bgcolor='#7f7f7f',
#     plot_bgcolor='#c7c7c7'
# )
#
#
# data = [trace, p]
# fig = dict(data=data, layout=layout)
# po.plot(fig, filename='error-bar-style')
