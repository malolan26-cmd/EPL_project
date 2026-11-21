import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
from etl import DB
st.set_page_config(page_title='Premier League 2025/26',layout='wide')
st.title('Premier League | 2025/26')
st.caption('Results-derived performance • Football-Data.co.uk • excludes administrative points adjustments')
@st.cache_data(ttl=300)
def load():
    engine=create_engine(DB)
    with engine.connect() as c:
        return pd.read_sql('SELECT * FROM team_summary WHERE season=2025 ORDER BY points DESC,gd DESC,gf DESC,team',c),pd.read_sql('SELECT * FROM team_trends WHERE season=2025 ORDER BY match_date,match_id',c)
try: summary, games=load()
except Exception as exc: st.error(f'Database unavailable. Run ETL first. {exc}'); st.stop()
if summary.empty: st.warning('No data. Run ETL first.'); st.stop()
team=st.sidebar.selectbox('Select team',sorted(summary.team))
venue=st.sidebar.radio('Venue',['All','Home','Away'])
selected=games[games.team.eq(team)]; filtered=selected if venue=='All' else selected[selected.venue.eq(venue)]
league, detail, compare=st.tabs(['League overview','Team performance','Compare teams'])
with league:
    st.dataframe(summary[['team','played','wins','draws','losses','points','gf','ga','gd']],hide_index=True,use_container_width=True)
    st.plotly_chart(px.scatter(summary,x='ga',y='gf',size='points',hover_name='team',labels={'ga':'Goals conceded','gf':'Goals scored'}),use_container_width=True)
with detail:
    st.header(team+' | '+venue)
    for col,label,value in zip(st.columns(4),['Points','Win rate','Goals scored','Goals conceded'],[filtered.points.sum(),f"{filtered.result.eq('W').mean():.0%}",filtered.gf.sum(),filtered.ga.sum()]): col.metric(label,value)
    st.caption('Season trajectory (all venues)')
    st.plotly_chart(px.line(selected,x='match_number',y='cumulative_points',markers=True),use_container_width=True)
    st.plotly_chart(px.line(selected,x='match_number',y='rolling_ppg',markers=True),use_container_width=True)
    st.plotly_chart(px.bar(filtered,x='match_date',y=['gf','ga'],barmode='group',hover_data=['opponent','venue']),use_container_width=True)
    st.plotly_chart(px.scatter(filtered,x='shots',y='gf',color='result',hover_data=['opponent','venue']),use_container_width=True)
    st.dataframe(filtered[['match_date','opponent','venue','result','gf','ga','shots','shots_on_target','corners','fouls','yellow_cards','red_cards']],hide_index=True)
    st.download_button('Export filtered matches',filtered.to_csv(index=False),'team_matches.csv','text/csv')
with compare:
    choices=st.multiselect('Teams',sorted(summary.team),default=[team]); comp=summary[summary.team.isin(choices)]
    metric=st.selectbox('Metric',['points','ppg','gf','ga','gd','shots_per_game','sot_per_game','clean_sheets','conversion_pct'])
    st.plotly_chart(px.bar(comp,x='team',y=metric),use_container_width=True)
    st.plotly_chart(px.line(games[games.team.isin(choices)],x='match_number',y='cumulative_points',color='team'),use_container_width=True)
