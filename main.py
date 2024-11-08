import streamlit as st
import pandas as pd
import requests
import json

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
st.title("All the squirrels in Central park, 2018")
st.map(df, longitude='x',latitude='y', size=1)