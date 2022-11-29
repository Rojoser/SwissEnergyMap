# Import
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
import json
from copy import deepcopy

from plotly.subplots import make_subplots

# Get data set and map
energy_raw = pd.read_csv('data/renewable_power_plants_CH.csv')
energy_dc = deepcopy(energy_raw)

with open("data/georef-switzerland-kanton.geojson") as response:
    cantons = json.load(response)

# Handle data - change canton code to canton name and grab only certain columns
cantons_dict = {'TG':'Thurgau', 'GR':'Graubünden', 'LU':'Luzern', 'BE':'Bern', 'VS':'Valais',
                'BL':'Basel-Landschaft', 'SO':'Solothurn', 'VD':'Vaud', 'SH':'Schaffhausen', 'ZH':'Zürich',
                'AG':'Aargau', 'UR':'Uri', 'NE':'Neuchâtel', 'TI':'Ticino', 'SG':'St. Gallen', 'GE':'Genève',
                'GL':'Glarus', 'JU':'Jura', 'ZG':'Zug', 'OW':'Obwalden', 'FR':'Fribourg', 'SZ':'Schwyz',
                'AR':'Appenzell Ausserrhoden', 'AI':'Appenzell Innerrhoden', 'NW':'Nidwalden', 'BS':'Basel-Stadt'}

energy_dc["canton_name"] = energy_dc["canton"].map(cantons_dict)
energy_df = energy_dc[['energy_source_level_2', 'electrical_capacity', 'lon', 'lat', 'municipality', 'canton_name', 'canton', 'commissioning_date', 'contract_period_end']]

# Set Streamlit title and header
st.set_page_config(page_title='Renewable Energy in Switzerland',
                   page_icon='random',
                   layout="centered")
st.title("Renewable Energy in Switzerland")
st.header("General Overview")

# Dataframe for General Overview
energy_overview = energy_df.groupby('energy_source_level_2').agg({'electrical_capacity': 'sum', 'municipality': 'count'})
energy_overview.rename({'electrical_capacity': 'Total Capacity', 'municipality': 'Number of Plants'},axis=1, inplace=True)

# Plot total capacity and number of sources for Switzerland
overview = make_subplots(rows=2, cols=2,
                         specs=[[{'rowspan':2}, {'rowspan': 2}],
                                                [None, None]],
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
overview.update_layout(title_text='Renewable Energy in Switzerland, overview',
                       title_font_size = 24,
                       showlegend=False)

st.plotly_chart(overview)


st.header("Geographical Analysis")
st.subheader("Energy Installed by Canton")

# Set Streamlit columns for widgets
left_column, right_column = st.columns([3, 2])

# Aggregation metric
agg_by = right_column.radio(label='Choose aggregation metric', options=['Total Capacity', 'Number of Plants'])

agg_by_dict ={'Total Capacity': 'sum',
              'Number of Plants': 'count'}

# Energy source
sources = left_column.multiselect('Select Renewal Sources',
                                  ['Bioenergy', 'Hydro', 'Solar', 'Wind'],
                                  ['Bioenergy', 'Hydro', 'Solar', 'Wind'])   # All as default value

energy_agg = energy_df[energy_df['energy_source_level_2'].isin(sources)]\
    .groupby(['canton_name']).agg({'electrical_capacity': agg_by_dict[agg_by]})
# Aggregate data
#if agg_by == 'Total Capacity':
#    energy_agg = energy_df.groupby(['canton_name']).agg({'electrical_capacity': 'sum'})
#else:
#    energy_agg = energy_df.groupby(['canton_name']).agg({'electrical_capacity': 'count'})


# General map - Energy Installed by Canton
energy_general = px.choropleth_mapbox(energy_agg,
                                      color='electrical_capacity',
                                      geojson=cantons,
                                      locations=energy_agg.index,
                                      featureidkey="properties.kan_name",
                                      center={"lat": 46.8, "lon": 8.3},
                                      mapbox_style="carto-positron",
                                      zoom=6,
                                      opacity=0.8,
                                      #width=500,
                                      height=3500,
                                      labels={"canton_name":"Canton",
                                              'electrical_capacity': agg_by,
                                              "count":"Number of Plants"},
                                      title="<b>Renewable Energy by Canton</b>",
                                      color_continuous_scale="Turbo"
                                      )
energy_general.update_layout(margin={"r":35,"t":35,"l":35,"b":35},
                             font={"family":"Sans",
                                   "color":"black"},
                             hoverlabel={"bgcolor":"white",
                                         "font_size":12,
                                         "font_family":"Sans"},
                             title={"font_size":20,
                                    "xanchor":"left", "x":0.01,
                                    "yanchor":"bottom", "y":0.95},
                             coloraxis_colorbar={'title': agg_by}
                             )

st.plotly_chart(energy_general)

st.subheader('Energy Plants in each Canton')

canton = st.selectbox("Select a Canton",
                      list(energy_df['canton_name'].unique()))

st.text(canton)
energy_detail_df = energy_df[energy_df['canton_name']==canton]

# Create a container for the plot
plot_spot = st.empty()

# General Map - Canton Detail
energy_detail_fig = px.scatter_mapbox(energy_detail_df,
                                      lat=energy_detail_df['lat'],
                                      lon=energy_detail_df['lon'],
                                      #custom_data=energy_detail_df['municipality'],
                                      hover_data={'municipality':True,
                                               'lat': False,
                                               'lon': False
                                               },
                                      color=energy_detail_df['energy_source_level_2'],
                                      #center={"lat": 46.8, "lon": 8.3},
                                      labels = {'energy_source_level_2': 'Renewal Source'},
                                      mapbox_style="carto-positron",
                                      zoom=7,
                                      opacity=0.8,
                                      width=500,
                                      height=3500,
                                      title="<b>Plants by Source in Canton</b>"
                                   )

energy_detail_fig.update_layout(margin={"r":35,"t":35,"l":35,"b":35},
                                font={"family":"Sans",
                                      "color":"black"},
                                hoverlabel={"bgcolor":"white",
                                            "font_size":12,
                                            "font_family":"Sans"},
                                title={"font_size":20,
                                       "xanchor":"left", "x":0.01,
                                       "yanchor":"bottom", "y":0.95},
                                coloraxis_colorbar={'title': 'Energy Source'}
                                )

# Fill the container with the plot with the canton updated
with plot_spot:
    st.plotly_chart(energy_detail_fig)

show_df = st.checkbox('Show Dataframe with Canton Plants')
if show_df:
    st.dataframe(energy_detail_df)
