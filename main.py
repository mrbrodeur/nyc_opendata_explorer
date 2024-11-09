import streamlit as st
import pandas as pd
import requests
import json
from st_aggrid import AgGrid

@st.cache_data()
def load_data():
    offset = 0
    squirrels = []
    while True:
        uri = f'https://data.cityofnewyork.us/resource/vfnx-vebw.json?$offset={offset}'
        r = requests.get(uri).json()
        if r:
            squirrels += r
            offset += 1000
        else:
            break
    df = pd.DataFrame.from_dict(squirrels)
    df['x'] = pd.to_numeric(df['x'])
    df['y'] = pd.to_numeric(df['y'])
    return df

df = load_data()

st.title("All the squirrels in Central park, 2018")

column_choices = df.columns.values.tolist()

column_choices = [item for item in column_choices if item not in ['x', 'y']]
column_choices = [item for item in column_choices if not item.startswith(':@')]
st.header("Table of squirrels")
options = st.multiselect(
    'Select a fields',
     column_choices, column_choices[:7])
st.dataframe(df[options])
st.header("Map of squirrels")
st.map(df, longitude='x',latitude='y', size=1)