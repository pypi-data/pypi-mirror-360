import numpy as np
import pandas as pd
import wsba_main as wsba
import data_pipelines as data
import numpy as np

season_load = wsba.repo_load_seasons()

select = season_load[9:17]

#pbp = data.load_pbp_db(select)

#wsba.wsba_xG(pbp,hypertune=True,train=True,train_runs=30,cv_runs=30)
#select = season_load[3:18]
#for season in select:
#    wsba.nhl_apply_xG(data.load_pbp([season])).to_parquet(f'pbp/parquet/nhl_pbp_{season}.parquet',index=False)
#data.pbp_db(select)

#test = pd.read_parquet('aws_pbp/20242025.parquet')
#wsba.roc_auc_curve(test,'tools/xg_model/wsba_xg.joblib')
#wsba.feature_importance('tools/xg_model/wsba_xg.joblib')
#wsba.reliability(test,'tools/xg_model/wsba_xg.joblib')

#data.build_stats(['skater','team','goalie'],select)
#data.game_log(['skater','goalie'],select)
#data.fix_names(['skater','goalie'],select)

## DATA EXPORT ##
#data.push_to_sheet(select,['skaters','team','info'])

wsba.nhl_scrape_game(['2024020008'],remove=[]).to_csv('wtfwhy.csv',index=False)

pbp = pd.read_parquet('pbp/parquet/nhl_pbp_20242025.parquet')
helle = pbp.loc[pbp['event_goalie_id']==8476945,
                ['game_id','period','seconds_elapsed',
                 'strength_state','event_type','description',
                 'event_goalie_id','x','y','xG']]
mp = pd.read_csv('shots_2024.csv')
goalie = mp.loc[mp['goalieIdForShot']==8476945,
                ['game_id','period','time','event','goalieIdForShot',
                 'xCord','yCord','xGoal']].replace({
                     'SHOT':'shot-on-goal',
                     'MISS':'missed-shot',
                     'GOAL':'goal'
                 })

helle.to_csv('hellebuyck.csv',index=False)
helle['game_id'] = helle['game_id'].astype(str)
goalie['game_id'] = ('20240'+goalie['game_id'].astype(str))
pd.merge(helle,goalie,how='left',left_on=['game_id','period','seconds_elapsed','event_type','x','y'],right_on=['game_id','period','time','event','xCord','yCord']).to_csv('test.csv',index=False)

