import os

opj = os.path.join
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.offline as po
import plotly.graph_objs as go

dir = '/DATA/projet/unesco/data/'
figdir=opj(dir,'fig')
file = 'data_chad_mission_2020.csv'
dateparser = lambda x: pd.datetime.strptime(x, "%d/%m/%Y")
df = pd.read_csv(opj(dir, file), header=0, parse_dates=True, date_parser=dateparser, index_col= 0)

df.plot.scatter(x='turbidity', y='chl-a', c='temperature', cmap=plt.cm.Spectral_r)
plt.savefig(opj(dir,'chl_vs_turbi_chad_2020.png'),dpi=300)
# prepare extraction file
df = df.reset_index()
df['Name'] = df['locality'] + '_' + df.index.astype('str')
df_ = df[['Name', 'longitude', 'latitude', 'date']]
df_.columns = ['Name', 'Lon', 'Lat', 'DateTime']
df_.to_csv(opj(dir, 'pixel_extract_chad2020.csv'), index=False, sep='\t', date_format='%Y-%m-%dT%H:%M:%S')

# do extraction with SNAP to get pixEx_unesco_org.esa.s2tbx.processor.mci.S2MciOp_measurements.txt
file = 'pixEx_2020_chad_org.esa.s2tbx.processor.mci.S2MciOp_measurements.txt'
sat = pd.read_csv(opj(dir, file), header=0, index_col=0, parse_dates=True, sep='\t', skiprows=7)
# file = 'pixEx_org.esa.s2tbx.processor.mci.S2MciOp_measurements_33PVQ.txt'
# sat = sat.append(pd.read_csv(opj(dir, file), header=0, index_col=0, parse_dates=True, sep='\t', skiprows=6))

matchup = sat.merge(df,on='Name')

matchup.plot.scatter(x='turb', y='chl_git2008_sunglint', c='spm', cmap=plt.cm.Spectral_r)
#sat.plot.scatter(x='turb', y='chl_git2008', c='spm', cmap=plt.cm.Spectral_r)
matchup.plot.scatter(x='chl-a', y='chl_git2008_sunglint', c='spm', cmap=plt.cm.Spectral_r)
matchup.plot.scatter(x='turbidity', y='turb', c='spm', cmap=plt.cm.Spectral_r)
matchup['sample_date'] = matchup['date'].dt.strftime('%Y-%m-%d')

params=(['turbidity', 'turb'],['chl-a', 'chl_git2008_sunglint'])
i=0
fig = px.scatter(matchup, x=params[i][0], y=params[i][1],  color='spm', hover_name="Name", hover_data=['CoordID','Date(yyyy-MM-dd)','sample_date','Name'],
                         trendline="ols", trendline_color_override='red',opacity=0.5,
                         range_x=[0,400],range_y=[0,400],height =900,width=1200)
fig.add_trace(
                go.Scatter(
                x=[-1000,1000],
                y=[-1000,1000],
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

fig.update_layout(title_font_size=24, margin=dict(l=265, r=200, t=100, b=100))
#fig.update_layout(title_font_size=24, margin=dict(l=300, r=20, t=200, b=20))
po.plot(fig,filename=opj(figdir,'matchup_chad_2020_'+params[i][0]+'.html'))