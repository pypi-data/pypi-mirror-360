import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import rink_plot
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter

def wsba_rink(setting='full', vertical=False):
    return rink_plot.rink(setting=setting, vertical=vertical)

def heatmap(df,goalie,team,events,strengths):
    df['event_team_abbr_2'] = np.where(df['home_team_abbr']==df['event_team_abbr'],df['away_team_abbr'],df['home_team_abbr'])
    df['strength_state_2'] = df['strength_state'].str[::-1]

    df = df.loc[(df['event_type'].isin(events))&(df['x_adj'].notna())&(df['y_adj'].notna())]
    df['x'] = np.where(df['x_adj']<0,-df['y_adj'],df['y_adj'])
    df['y'] = abs(df['x_adj'])
    df['event_distance'] = abs(df['event_distance'].fillna(0))
    df = df.loc[(df['event_distance']<=89)&(df['y']<=89)&(df['empty_net']==0)]

    y_min = 0
    y_max = 100

    df['G'] = (df['event_type']=='goal').astype(int)
    df['strength_state_2'] = np.where(df['strength_state_2'].isin(['5v5','5v4','4v5']),df['strength_state_2'],'Other')
        
    if strengths != 'all':
        df = df.loc[((df['strength_state_2'].isin(strengths)))]

    [x,y] = np.round(np.meshgrid(np.linspace(-42.5,42.5,85),np.linspace(y_min,y_max,(y_max-y_min))))
    xgoals = griddata((df['x'],df['y']),df['xG']-df['G'],(x,y),method='cubic',fill_value=0)
    xgoals_smooth = gaussian_filter(xgoals,sigma=3)

    player_shots = df.loc[(df['event_goalie_id'].astype(str).str.contains(goalie))&(df['event_team_abbr_2']==team)]
    [x,y] = np.round(np.meshgrid(np.linspace(-42.5,42.5,85),np.linspace(y_min,y_max,(y_max-y_min))))
    xgoals_player = griddata((player_shots['x'],player_shots['y']),player_shots['xG']-player_shots['G'],(x,y),method='cubic',fill_value=0)

    difference = (gaussian_filter(xgoals_player,sigma = 3)) - xgoals_smooth
    data_min= difference.min()
    data_max= difference.max()
   
    if abs(data_min) > data_max:
        data_max = data_min * -1
    elif data_max > abs(data_min):
        data_min = data_max * -1

    fig = go.Figure(
        data = go.Contour(  x=np.linspace(-42.5,42,5,85),
                            y=np.linspace(y_min,y_max,(y_max-y_min)),
                            z=xgoals_smooth,
                            colorscale=[[0.0,'red'],[0.5,'#09090b'],[1.0,'blue']],
                            connectgaps=True,
                            contours=dict(
                                type='levels',
                                start = data_min,
                                end = data_max,
                                size=(data_max-data_min)/11
                            ),
                            colorbar=dict(
                                len = 0.7,
                                orientation='h',
                                showticklabels=False,
                                thickness=15,
                                yref='paper',
                                yanchor='top',
                                y=0
                            ))
    )

    return fig