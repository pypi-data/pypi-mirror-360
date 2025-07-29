import os
import numpy as np
import pandas as pd
import wsba_main as wsba
import numpy as np
from datetime import datetime
from gspread_pandas import Spread
import matplotlib.pyplot as plt
from scipy import stats

### DATA PIPELINES ###

def pbp(seasons):
    for season in seasons:
        errors=[]
        for season in seasons:
            data = wsba.nhl_scrape_season(season,remove=[],local=True,sources=True,errors=True)
            errors.append(data['errors'])
            data['pbp'].to_csv(f'pbp/nhl_pbp_{season}.csv',index=False)
            pd.read_csv(f'pbp/nhl_pbp_{season}.csv').to_parquet(f'pbp/parquet/nhl_pbp_{season}.parquet',index=False)
        print(f'Errors: {errors}')

def pbp_db(seasons):
    for season in seasons:
        pbp = pd.read_parquet(f'pbp/parquet/nhl_pbp_{season}.parquet')
        pbp.loc[pbp['event_type'].isin(wsba.events+['penalty'])].to_csv('temp.csv',index=False)
        pd.read_csv('temp.csv').to_parquet(f'aws_pbp/{season}.parquet',index=False)
        os.remove('temp.csv')

def load_pbp(seasons):
    return pd.concat([pd.read_parquet(f'pbp/parquet/nhl_pbp_{season}.parquet') for season in seasons])

def load_pbp_db(seasons):
    return pd.concat([pd.read_parquet(f'aws_pbp/{season}.parquet') for season in seasons])

def build_stats(arg,seasons):
    #Stats building
    for group in arg:
        for season in seasons:
            pbp = pd.read_parquet(f'pbp/parquet/nhl_pbp_{season}.parquet')
            strengths = pbp.loc[~(pbp['strength_state'].isin(['5v5','5v4','4v5'])),'strength_state'].drop_duplicates().to_list()
            dfs = []
            for strength in [['5v5'],['5v4'],['4v5'],strengths,'all']:
                for season_type in [[2],[3]]:
                    data = wsba.nhl_calculate_stats(pbp,group,season_type,strength,shot_impact=True)
                    if strength != 'all':
                        if len(strength) > 1:
                            data['Strength'] = 'Other'
                        else:
                            data['Strength'] = strength[0]
                    else:
                        data['Strength'] = 'All'
                    data['Span'] = season_type[0]
                    dfs.append(data)
            stat = pd.concat(dfs)
            stat.to_csv(f'stats/{group}/wsba_nhl_{season}_{group}.csv',index=False)
    
def game_log(arg,seasons):
    #Stats building
    for group in arg:
        for season in seasons:
            pbp = pd.read_parquet(f'pbp/parquet/nhl_pbp_{season}.parquet')
            strengths = pbp.loc[~(pbp['strength_state'].isin(['5v5','5v4','4v5'])),'strength_state'].drop_duplicates().to_list()
            dfs = []
            for strength in [['5v5'],['5v4'],['4v5'],strengths,'all']:
                for season_type in [[2],[3]]:
                    data = wsba.nhl_calculate_stats(pbp,group,season_type,strength,split_game=True,shot_impact=False)
                    if strength != 'all':
                        if len(strength) > 1:
                            data['Strength'] = 'Other'
                        else:
                            data['Strength'] = strength[0]
                    else:
                        data['Strength'] = 'All'
                    data['Span'] = season_type[0]
                    dfs.append(data)
            stat = pd.concat(dfs)
            path = 'stats/game_log' if group == 'skater' else 'stats/game_log/goalie'
            stat.to_csv(f'{path}/temp.csv',index=False)
            stats = pd.read_csv(f'{path}/temp.csv')
            os.remove('temp.csv')
            stats.to_parquet(f'{path}/wsba_nhl_{season}_game_log{'_goalie' if group == 'goalie' else ''}.parquet',index=False)

def fix_names(arg,seasons):
    #Stats building
    for group in arg:
        for season in seasons:
            print(f'Fixing names for {group} stats in {season}...')

            group_name = 'Player' if 'skater' in group else 'Goalie'
            if 'game_log' in group:
                if 'skater' in group:
                    path = f'stats/{group[-8:]}/wsba_nhl_{season}_game_log.parquet'
                else:
                    path = f'stats/{group[-8:]}/goalie/wsba_nhl_{season}_game_log_goalie.parquet'
            else:
                path = f'stats/{group}/wsba_nhl_{season}_{group}.csv'
            
            if 'game_log' in group:
                stats = pd.read_parquet(path)
            else:
                stats = pd.read_csv(path)

            missing  = stats.loc[stats[group_name].astype(str)=='0','ID'].drop_duplicates()

            if not missing.to_list():
                ''
            else:
                info = wsba.nhl_scrape_player_data(missing)
                columns={'playerId':'ID',
                                'fullName':group_name,
                                'position':'Position',
                                'headshot':'Headshot',
                                'shootsCatches':'Handedness',
                                'heightInInches':'Height (in)',
                                'weightInPounds':'Weight (lbs)',
                                'birthDate':'Birthday' }
                
                info = info[list(columns.keys())]
                complete = pd.merge(stats,info,how='left',left_on=['ID'],right_on=['playerId']).replace({'0':np.nan})
                
                for key, value in zip(columns.keys(), columns.values()):
                    complete[value] = complete[value].combine_first(complete[key])
                    complete = complete.drop(columns=[key])

                complete.to_csv('wtf.csv')
                #Add player age
                complete['Birthday'] = pd.to_datetime(complete['Birthday'],format='mixed')
                complete['season_year'] = complete['Season'].astype(str).str[4:8].astype(int)
                complete['Age'] = complete['season_year'] - complete['Birthday'].dt.year

                complete['WSBA'] = complete[group_name]+complete['Team']+complete['Season'].astype(str)
                complete = complete.sort_values(by=['Player','Season','Team','ID'])
                
                if 'game_log' in group:
                    complete.to_csv('temp.csv',index=False)
                    pd.read_csv('temp.csv').to_parquet(path,index=False)
                    os.remove('temp.csv')

                else:
                    complete.to_csv(path)

def push_to_sheet(seasons, types = ['skaters','team','goalie','info'], msg = 'Data Update'):
    spread = Spread('WSBA - NHL 5v5 Shooting Metrics Public v1.0')

    if 'skaters' in types:
        #Tables
        skater = pd.concat([pd.read_csv(f'stats/skater/wsba_nhl_{season}_skater.csv') for season in seasons])
        skater = skater.loc[(skater['Strength']=='5v5')&(skater['Span']==2)]

        spread.df_to_sheet(skater,index=False,sheet='Skaters DB')
    
    if 'team' in types:
        team = pd.concat([pd.read_csv(f'stats/team/wsba_nhl_{season}_team.csv') for season in seasons])
        team = team.loc[(team['Strength']=='5v5')&(team['Span']==2)]

        spread.df_to_sheet(team,index=False,sheet='Teams DB')

    if 'goalie' in types:
        goalie = pd.concat([pd.read_csv(f'stats/skater/wsba_nhl_{season}_goalie.csv') for season in seasons])
        goalie = goalie.loc[(goalie['Strength']=='5v5')&(goalie['Span']==2)]

        spread.df_to_sheet(goalie,index=False,sheet='Goalie DB')

    if 'info' in types:
        team_info = pd.read_csv('tools/teaminfo/nhl_teaminfo.csv')
        country = pd.read_csv('tools/teaminfo/nhl_countryinfo.csv')

        spread.df_to_sheet(team_info,index=False,sheet='Team Info')
        spread.df_to_sheet(country,index=False,sheet='Country Info')   
        
    #if 'schedule' in types:
    #    schedule = pd.read_csv('schedule/schedule.csv')
    #
    #    spread.df_to_sheet(schedule,index=False,sheet='Schedule')

    log = spread.sheet_to_df(0,1,2,sheet='Update Log')
    update = pd.DataFrame({'Date/Time (US-Central)':[datetime.now()],
                           'Change':[msg]})

    spread.df_to_sheet(pd.concat([log,update]),index=False,start='A2',sheet='Update Log')

    print('Done.')

def compare_xG(seasons):
    load_1 = pd.concat([pd.read_csv(f'stats/skater/wsba_nhl_{season}_skater.csv') for season in seasons])
    load_2 = pd.read_csv('stats/moneypuck/moneypuck.csv')

    dfs = []
    for strength in [('5v5','5on5'),('5v4','5on4'),('4v5','4on5'),('Other','other'),('All','all')]:  
        df = load_1
        mp = load_2

        df = df.loc[(df['Span']==2)&(df['Strength']==strength[0])][['ID','Season','xGi','Gi']].replace({
            20162017:2016,
            20172018:2017,
            20182019:2018,
            20192020:2019,
            20202021:2020,
            20212022:2021,
            20222023:2022,
            20232024:2023
        })
        mp = mp.loc[(mp['situation'])==strength[1]][['playerId','season','I_F_xGoals','I_F_goals']].rename(columns={'playerId':'ID','season':'Season','I_F_xGoals':'ixG','I_F_goals':'G'})

        merge = pd.merge(df,mp,how='left')
        merge = merge.dropna()

        x = merge['xGi']
        y = merge['ixG']

        r,p = stats.pearsonr(x,y)
        plt.scatter(x,y,label=f'r = {r:.4f}')
        plt.title(f'WSBA xG vs MoneyPuck xG (2016-17 to 2023-24 in {strength[0]} situations)')
        plt.xlabel('WSBA xG')
        plt.ylabel('MoneyPuck xG')
        plt.legend(loc="lower right")
        plt.savefig(f'tools/xg_model/metrics/moneypuck/wsba_vs_moneypuck_{strength[0]}.png')
        plt.close()
        
        for xg,model in [(df,'WSBA'),(mp,'MoneyPuck')]:
            xg = xg.rename(columns={'xGi':'ixG','Gi':'G'})

            x = xg['ixG']
            y = xg['G']

            r,p = stats.pearsonr(x,y)
            plt.scatter(x,y,label=f'r = {r:.4f}')
            plt.title(f'{model} xG vs Goals (2016-17 to 2023-24 in {strength[0]} situations)')
            plt.xlabel(f'{model}')
            plt.ylabel('Goals')
            plt.legend(loc="lower right")
            plt.savefig(f'tools/xg_model/metrics/predict_power/{model}_predict_power_{strength[0]}.png')
            plt.close()

        dfs.append(pd.DataFrame([
            {   'Strength':strength[0],
                'WSBA G-xG':np.mean(df['Gi']-df['xGi']),
                'MoneyPuck G-xG':np.mean(mp['G']-mp['ixG'])
            }
            ]
        ))
        
        compare = pd.concat(dfs)
        compare['Compare'] = np.where(abs(compare['WSBA G-xG'])<abs(compare['MoneyPuck G-xG']),'WSBA','MoneyPuck')
        compare.to_csv('tools/xg_model/metrics/predict_power/wsba_vs_moneypuck_predict_power.csv',index=False)