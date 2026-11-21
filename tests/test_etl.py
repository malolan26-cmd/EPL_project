import pandas as pd
import pytest
from etl import transform, STATS

def sample():
    rows=[]
    for a in range(20):
        for b in range(20):
            if a==b: continue
            r={'Date':'01/01/2026','HomeTeam':f'Team {a}','AwayTeam':f'Team {b}','FTHG':2,'FTAG':1}
            r.update({c:5 for pair in STATS.values() for c in pair}); rows.append(r)
    return pd.DataFrame(rows)

def test_complete():
    t,m,s=transform(sample()); assert (len(t),len(m),len(s))==(20,380,760); assert m.home_goals.sum()==760

def test_incomplete():
    with pytest.raises(ValueError): transform(sample().iloc[:-1])

def test_duplicate():
    x=sample(); x.iloc[-1]=x.iloc[0]
    with pytest.raises(ValueError): transform(x)
