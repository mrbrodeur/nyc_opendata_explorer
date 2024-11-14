import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

df = pd.read_json('data.json')
df['view'] = '/view?id=' + df['id']
df = df[df['dataset_type'].isin(['Dataset'])]
df.sort_values('name', inplace=True)
df_filtered = df
row_count = len(df)
categories = ['Transportation', 'City Government', 'Housing & Development',
 'Social Services', 'Public Safety', 'Health', 'Environment', 'Education',
 'Business', 'Recreation', 'NYC BigApps']
# dataset_types = ['Dataset', 'Map', 'Filtered View', 'File or Document', 'Story', 'External Link', 'Chart', None]
cat_selected = None
type_selected = None
dataframe_params = {
    'data': df_filtered,
    'column_order': ['name', 'category', 'views', 'updated', 'view'],
    'column_config': {
        'view': st.column_config.LinkColumn('View', display_text='Explore'),
    },
    'height': 800,
    'use_container_width': True,
    'hide_index': True,
}

st.title("NYC Opendata Explorer")
st.markdown("This app is a visualizer for [NYC Open Data](http://opendata.cityofnewyork.us/). Some of the datasets are VERY large, so please be patient and let it load. It may take a few minutes.")

with st.container(border=True):
    st.header('Filters')
    cat_selected = st.pills('Filter by category...', categories)
    # type_selected = st.pills('Filter by dataset type...', dataset_types)
    text_filter = st.text_input("Filter by name")

    if st.button('Reset Filters'):
        df_filtered = df
        text_filter = None
        cat_selected = None
        type_selected = None

st.header('Datasets')

counter_metric = st.metric(label='Number of datasets', value=len(df_filtered))

main_table = st.dataframe(**dataframe_params)

if cat_selected:
    dataframe_params['data'] = df_filtered[df_filtered['category'] == cat_selected]
    main_table.dataframe(**dataframe_params)
    counter_metric.metric(label='Number of datasets', value=len(dataframe_params['data']))

if text_filter:
    dataframe_params['data'] = df_filtered[df_filtered['name'].str.contains(text_filter.strip(), case=False)]
    main_table.dataframe(**dataframe_params)
    counter_metric.metric(label='Number of datasets', value=len(dataframe_params['data']))

# if type_selected:
#     dataframe_params['data'] = df_filtered[df_filtered['dataset_type'] == type_selected]
#     main_table.dataframe(**dataframe_params)
#     counter_metric.metric(label='Number of datasets', value=len(dataframe_params['data']))

