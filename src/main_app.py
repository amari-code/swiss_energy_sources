import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import json
from copy import deepcopy

st.set_page_config(layout="wide")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df


with open('./data/georef-switzerland-kanton.geojson', encoding='UTF-8') as f:
    sw_gj = json.load(f)

pplants_raw = load_data(path="./data/renewable_power_plants_CH.csv")
pplants = deepcopy(pplants_raw)

with open('./data/cantons_dict.json', 'r', encoding='UTF-8') as p:
    cantons_dict = json.load(p)

pplants['canton_name']=pplants['canton'].map(cantons_dict)


pplants_group_energy_production = pplants.groupby(['canton_name','energy_source_level_2']).agg(total_production=('production', 'sum')).reset_index()

def best_source(c_name):
    for c in c_name.unique():
        bs = pplants_group_energy_production.loc[pplants_group_energy_production[pplants_group_energy_production['canton_name']==c]['total_production'].idxmax()]
    return bs.values

pplants_group_main_sources = pplants.groupby('canton_name').agg(total_production=('production', np.sum),
                                                     total_capacity=('electrical_capacity', np.sum),
                                                     best_energy_source=('canton_name', best_source)).reset_index()

pplants_group_main_sources[['canton_name_2','best_source', 'best_source_production']] = pd.DataFrame(pplants_group_main_sources.best_energy_source.to_list())
pplants_group_main_sources = pplants_group_main_sources.drop(['canton_name_2','best_energy_source'], axis=1)
pplants_group_main_sources['best_source'] = pplants_group_main_sources['best_source'].astype(str)


# st.title("Swiss Energy Sources")
st.markdown("<h1 style='text-align: center; color: dark-grey;'>Swiss Energy Sources</h1>", unsafe_allow_html=True)

# st.dataframe(data=pplants_group_main_sources)

plot_type = ['Total Production', 'Main Source Production']


plot_type_sel = st.selectbox("Choose a Plot", plot_type)


main_source_fig = px.choropleth_mapbox(pplants_group_main_sources, geojson=sw_gj, featureidkey="properties.kan_name", locations='canton_name', color='best_source',
                            color_discrete_sequence=['#9ecae1', '#ffeda0', '#deebf7', '#a1d99b'],
                        #    range_color=(pplants.production.min(), pplants.production.max()),
                           mapbox_style="carto-positron",
                            zoom=7, center = {"lat": 46.92739, "lon":  8.41028},
                           opacity=0.5,
                           hover_data={
                                       'canton_name' : False,
                                       'best_source_production': ':,.2f',
                                       'total_production': ':,.2f'
                                       },
                           labels={
                               'best_source' : 'Main source',
                               'best_source_production' : 'Main Source Energy Production (MWh)',
                               'total_production': 'Total Canton Energy Production (MWh)'
                           },
                            title="<b>Main Energy Sources per Canton</b>",
                           hover_name="canton_name"
                          )
main_source_fig.update_layout(height=800)



production_fig = px.choropleth_mapbox(pplants_group_main_sources, 
                                      geojson=sw_gj, 
                                      featureidkey="properties.kan_name", 
                                      locations='canton_name', 
                                      color='total_production',
                                      color_continuous_scale=px.colors.sequential.Viridis,
                                      mapbox_style="carto-positron",
                                      zoom=7, 
                                      center = {"lat": 46.92739, "lon":  8.41028},
                                      opacity=0.5,
                                      hover_data={
                                       'canton_name' : False,
                                       'best_source': True,
                                       'total_production': ':,.2f'
                                       },
                                       labels={
                                           'best_source' : 'Main source',
                                           'total_production': 'Total Canton Energy Production (MWh)'
                                           },
                                           title="<b>Total Energy Production per Canton</b>",
                                           hover_name="canton_name"
                                           )

production_fig.update_layout(height=800)

if plot_type_sel == 'Total Production':
    st.plotly_chart(production_fig, use_container_width=True)
else:
    st.plotly_chart(main_source_fig, use_container_width=True)

