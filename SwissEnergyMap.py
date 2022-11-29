# Import
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
#pio.renderers.default = 'colab'   # try changing this in case your plots aren't shown
import pandas as pd
import json

from plotly.subplots import make_subplots

# Get data set and map
energy_raw = pd.read_csv('data/renewable_power_plants_CH.csv')

with open("data/georef-switzerland-kanton.geojson") as response:
    cantons = json.load(response)

# Handle data - change canton code to canton name and grab only certain columns
cantons_dict = {'TG':'Thurgau', 'GR':'Graubünden', 'LU':'Luzern', 'BE':'Bern', 'VS':'Valais',
                'BL':'Basel-Landschaft', 'SO':'Solothurn', 'VD':'Vaud', 'SH':'Schaffhausen', 'ZH':'Zürich',
                'AG':'Aargau', 'UR':'Uri', 'NE':'Neuchâtel', 'TI':'Ticino', 'SG':'St. Gallen', 'GE':'Genève',
                'GL':'Glarus', 'JU':'Jura', 'ZG':'Zug', 'OW':'Obwalden', 'FR':'Fribourg', 'SZ':'Schwyz',
                'AR':'Appenzell Ausserrhoden', 'AI':'Appenzell Innerrhoden', 'NW':'Nidwalden', 'BS':'Basel-Stadt'}
energy_raw["canton_name"] = energy_raw["canton"].map(cantons_dict)
energy_df = energy_raw[['energy_source_level_2', 'electrical_capacity', 'lon', 'lat', 'municipality', 'canton_name', 'canton', 'commissioning_date', 'contract_period_end']]

# Set Streamlit title and header
st.title("Clean Energy in Switzerland")
st.header("General Overview")

# Dataframe for General Overview
energy_overview = energy_df.groupby('energy_source_level_2').agg({'electrical_capacity': 'sum', 'municipality': 'count'})
energy_overview.rename({'electrical_capacity': 'Total Capacity', 'municipality': 'Number of Plants'},axis=1, inplace=True)

# Plot total capacity and number of sources for Switzerland
overview = make_subplots(rows=1, cols=2,
                         subplot_titles=('Total Capacity by Source', 'Number of Plants by Source'))

overview.add_trace(go.Bar(x=energy_overview.index,
                          y=energy_overview['Total Capacity'],
                          marker_color='#4daf4a'),
                   row=1, col=1)
overview.add_trace(go.Bar(x=energy_overview.index,
                          y=energy_overview['Number of Plants'],
                          marker_color='#377eb8'),
                   row=1, col=2)
overview.update_traces(marker_line_color='#000000',
                       marker_line_width=2, opacity=0.8)
overview.update_layout(title_text='Switzerland Renewable Energy', showlegend=False)

st.plotly_chart(overview)


st.header("Analysis by Canton")

# Set Streamlit columns for widgets
left_column, right_column = st.columns([3, 2])

# Aggregation metric
agg_by = right_column.radio(label='Choose aggregation metric', options=['Total Capacity', 'Number of sources'])

agg_by_dict ={'Total Capacity': 'sum',
              'Number of sources': 'count'}

# Energy source
sources = left_column.multiselect('Select Renewal Sources',
    ['Bioenergy', 'Hydro', 'Solar', 'Wind'])

energy_agg = energy_df[energy_df['energy_source_level_2'].isin(sources)]\
    .groupby(['canton_name']).agg({'electrical_capacity': agg_by_dict[agg_by]})
# Aggregate data
#if agg_by == 'Total Capacity':
#    energy_agg = energy_df.groupby(['canton_name']).agg({'electrical_capacity': 'sum'})
#else:
#    energy_agg = energy_df.groupby(['canton_name']).agg({'electrical_capacity': 'count'})


# General map
energy_general = px.choropleth_mapbox(
        energy_agg,
        color='electrical_capacity',
        geojson=cantons,
        locations=energy_agg.index,
        featureidkey="properties.kan_name",
        center={"lat": 46.8, "lon": 8.3},
        mapbox_style="carto-positron",
        zoom=6,
        opacity=0.8,
        width=1200,
        height=800,
        labels={"canton_name":"Canton",
                "count":"Number of Plants"},
        title="<b>Clean Energy by Canton</b>",
        color_continuous_scale="Turbo",
)
energy_general.update_layout(margin={"r":35,"t":35,"l":35,"b":35},
                  font={"family":"Sans",
                       "color":"black"},
                  hoverlabel={"bgcolor":"white",
                              "font_size":12,
                             "font_family":"Sans"},
                  title={"font_size":20,
                        "xanchor":"left", "x":0.01,
                        "yanchor":"bottom", "y":0.95}
                 )
#energy_general.show()

st.plotly_chart(energy_general)
