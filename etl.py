import os, io, logging
from pathlib import Path
import pandas as pd
import requests
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent
SEASON = 2025
URL = 'https://www.football-data.co.uk/mmz4281/2526/E0.csv'
API = 'https://v3.football.api-sports.io'
DB = os.getenv('DATABASE_URL', 'postgresql+psycopg://football:football@localhost:5432/football')
STATS = {'shots':('HS','AS'), 'shots_on_target':('HST','AST'), 'corners':('HC','AC'), 'fouls':('HF','AF'), 'yellow_cards':('HY','AY'), 'red_cards':('HR','AR')}

def download():
    local = os.getenv('SOURCE_CSV')
    if local: return pd.read_csv(local)
    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    return pd.read_csv(io.BytesIO(response.content))

def transform(raw):
    required = ['Date','HomeTeam','AwayTeam','FTHG','FTAG'] + [c for pair in STATS.values() for c in pair]
    if not set(required).issubset(raw.columns): raise ValueError('Missing required source columns')
    d = raw[required].dropna(subset=['HomeTeam','AwayTeam','FTHG','FTAG']).copy()
    d['Date'] = pd.to_datetime(d.Date, dayfirst=True, format='mixed', errors='raise').dt.date
    names = sorted(set(d.HomeTeam) | set(d.AwayTeam))
    if len(d)!=380 or len(names)!=20 or d.duplicated(['HomeTeam','AwayTeam']).any() or (d.HomeTeam==d.AwayTeam).any(): raise ValueError('Expected a complete 20-team, 380-match double round robin')
    if not (d.HomeTeam.value_counts().eq(19).all() and d.AwayTeam.value_counts().eq(19).all()): raise ValueError('Invalid home/away counts')
    for c in required[3:]:
        d[c]=pd.to_numeric(d[c], errors='raise')
        if (d[c].dropna()<0).any() or (d[c].dropna()%1!=0).any(): raise ValueError(f'Invalid statistic: {c}')
    teams=pd.DataFrame({'team_id':range(1,21),'name':names}); ids=dict(zip(names,teams.team_id))
    d=d.sort_values(['Date','HomeTeam','AwayTeam']).reset_index(drop=True)
    matches=pd.DataFrame({'season':SEASON,'match_id':range(1,381),'match_date':d.Date,'home_id':d.HomeTeam.map(ids),'away_id':d.AwayTeam.map(ids),'home_goals':d.FTHG.astype(int),'away_goals':d.FTAG.astype(int)})
    rows=[]
    for i,r in d.iterrows():
        for side in (0,1):
            row={'season':SEASON,'match_id':i+1,'team_id':ids[r.HomeTeam if side==0 else r.AwayTeam]}
            row.update({k:r[v[side]] for k,v in STATS.items()}); rows.append(row)
    return teams,matches,pd.DataFrame(rows)

def api_fixtures():
    key=os.getenv('FOOTBALL_API_KEY')
    if not key: raise ValueError('Set FOOTBALL_API_KEY')
    r=requests.get(API+'/fixtures',headers={'x-apisports-key':key},params={'league':39,'season':SEASON},timeout=60); r.raise_for_status(); payload=r.json()
    if payload.get('errors'): raise RuntimeError(str(payload['errors']))
    fixtures=payload['response']
    if len(fixtures)!=380 or any(f['fixture']['status']['short'] not in ('FT','AET','PEN') for f in fixtures): raise ValueError('API season incomplete or inaccessible')
    return pd.DataFrame([{'api_id':f['fixture']['id'],'home':f['teams']['home']['name'],'away':f['teams']['away']['name'],'home_goals':f['goals']['home'],'away_goals':f['goals']['away']} for f in fixtures])

def run():
    teams,matches,stats=transform(download())
    engine=create_engine(DB)
    with engine.begin() as conn:
        conn.execute(text((ROOT/'schema.sql').read_text()))
        conn.execute(text('DELETE FROM match_stats WHERE season=2025; DELETE FROM matches WHERE season=2025; DELETE FROM teams WHERE season=2025'))
        teams.assign(season=SEASON).to_sql('teams',conn,if_exists='append',index=False)
        matches.to_sql('matches',conn,if_exists='append',index=False)
        stats.to_sql('match_stats',conn,if_exists='append',index=False)
    logging.info('Loaded %s teams, %s matches, %s team-match rows',len(teams),len(matches),len(stats))

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    run()
