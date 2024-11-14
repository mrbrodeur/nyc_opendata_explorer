import streamlit as st
import pydeck as pdk
import pandas as pd
import requests
import json

st.set_page_config(layout="wide")

data_id = st.query_params.get("id")

@st.cache_data()
def load_data(data_id):
    offset = 0
    data_rows = []
    while True:
        uri = f'https://data.cityofnewyork.us/resource/{data_id}.json?$offset={offset}'
        r = requests.get(uri).json()
        if r:
            data_rows += r
            offset += 1000
        else:
            break
    df = pd.DataFrame.from_dict(data_rows)
    return df

if data_id:
    df = load_data(data_id)
else:
    st.warning('No dataset selected. Please go back.')

metadata = pd.read_json('data.json')
metadata = metadata[metadata['id'] == data_id].to_dict('records')[0]

st.page_link("menu.py", label="Dataset Index", icon="⬅️")
st.title(metadata['name'])
with st.container(border=True):
    st.text(metadata['description'])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader(metadata['category'])
        st.caption("Category")

    with col2:
        st.subheader(metadata['views'])
        st.caption("Views")

    with col3:
        st.subheader(metadata['updated'])
        st.caption("Last Updated")


column_choices = df.columns.values.tolist()

column_choices = [item for item in column_choices if item not in ['x', 'y']]
column_choices = [item for item in column_choices if not item.startswith(':@')]
st.header("Table")
options = st.multiselect(
    'Select which columns to show (showing first 6 by default)',
     column_choices, column_choices[:7])
st.dataframe(df[options], hide_index=True)

latitude = None
longitude = None
for column in df.columns:
    try:
        min_val = df[column].astype(float).min()
        max_val = df[column].astype(float).min()

        if min_val > 40 and max_val < 41:
            latitude = column
        if min_val > -74.5 and min_val < -73.5:
            longitude = column 
    except:
        pass

print([latitude, longitude])

if latitude and longitude:
    df_coordinates = df.dropna(subset=[latitude, longitude], how='any')
    df_coordinates[latitude] = df_coordinates[latitude].astype(float)
    df_coordinates[longitude] = df_coordinates[longitude].astype(float)
    st.divider()
    st.header("Map")
    # st.map(df_coordinates, longitude=longitude,latitude=latitude, size=1)

    options = df_coordinates.columns
    selection = st.segmented_control(
        "Select data to show on map", options, selection_mode="multi",

    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        df_coordinates,
        get_position=f"[{longitude}, {latitude}]",
        get_radius=100,
        get_color=[255, 0, 0, 140],
        pickable=True,
    )
    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=df_coordinates[longitude].mean(), latitude=df_coordinates[latitude].mean(), zoom=10, min_zoom=6, max_zoom=15, pitch=0, bearing=0
    )

    tooltip_html = "<div style='max-width:250px'>" + "".join([f"<p>{{{s}}}</p>" for s in selection]) + "</div>"
    print(tooltip_html)

    # Combined all of it and render a viewport
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"html": tooltip_html, "style": {"color": "white"}},
    )
    st.pydeck_chart(r, height=600)
    # update_map()