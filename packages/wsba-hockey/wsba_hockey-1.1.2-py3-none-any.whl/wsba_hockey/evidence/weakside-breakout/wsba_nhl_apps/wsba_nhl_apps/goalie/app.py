import pandas as pd
import plot as wsba_plt
import numpy as np
from urllib.parse import *
from shiny import *
from shinywidgets import output_widget, render_widget

app_ui = ui.page_fluid(
    ui.tags.style(
    "body {background:#09090b"
    "}"
    ),
    output_widget("plot_goalie"),
)

def server(input, output, session):
    @output()
    @render_widget
    def plot_goalie():
        #Retreive query parameters
        search = session.input[".clientdata_url_search"]()
        query = parse_qs(urlparse(search).query)
        
        print(query)
        #If no input data is provided automatically provide a select goalie and plot all 5v5 fenwick shots
        defaults = {
            'goalie':['8471679'],
            'season':['20142015'],
            'team':['MTL'],
            'strength_state':['5v5'],
            'season_type':['2']
        }
        
        for key in defaults.keys():
            if key not in query.keys():
                query.update({key:defaults[key]})

        #Iterate through query and parse params with multiple selections
        for param in query.keys():
            q_string = query[param][0]
            query[param] = q_string.split(',')

        print(query)
        #Determine which season to load based on the input
        season = query['season'][0]
        #Load appropriate dataframe
        df = pd.read_parquet(f'https://weakside-breakout.s3.us-east-2.amazonaws.com/pbp/{season}.parquet')
        
        #Prepare dataframe for plotting based on URL parameters
        df = df.loc[(df['season'].astype(str).isin(query['season']))&(df['season_type'].astype(str).isin(query['season_type']))].replace({np.nan: None})
        #Return empty rink if no data exists else continue
        if df.empty:
            return wsba_plt.wsba_rink(setting='offense',vertical=True)
        else:
            rink = wsba_plt.wsba_rink(setting='offense',vertical=True)

            try:
                plot = wsba_plt.heatmap(df,goalie=query['goalie'][0],team=query['team'][0],events=['missed-shot','shot-on-goal','goal'],strengths=query['strength_state'])

                for trace in plot.data:
                    rink.add_trace(trace)

                player = query['goalie'][0]
                season = int(season[0:4])
                team = query['team'][0]
                strengths = 'All Situations' if len(query['strength_state']) == 4 else query['strength_state']
                span = 'Regular Season' if query['season_type'][0]=='2' else 'Playoffs'

                return rink.update_layout( 
                    title=dict(
                        text=f'{player} GSAx at {strengths}; {season}-{season+1}, {span}, {team}',
                        x=0.5, y=0.96,
                        xanchor='center',
                        yanchor='top',
                        font=dict(color='white')
                    ),
                ).add_annotation(
                    text='Lower GSAx',
                    xref="paper",
                    yref="paper",
                    xanchor='right',
                    yanchor='top',
                    font=dict(color='white'),
                    x=0.3,
                    y=0.04,
                    showarrow=False
                ).add_annotation(
                    text='Higher GSAx',
                    xref="paper",
                    yref="paper",
                    xanchor='right',
                    yanchor='top',
                    font=dict(color='white'),
                    x=0.76,
                    y=0.04,
                    showarrow=False
                )
            except:
                return wsba_plt.wsba_rink(setting='offense',vertical=True)

app = App(app_ui, server)