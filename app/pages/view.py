import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import requests
import functions

st.set_page_config(layout="wide")

data_id = st.query_params.get("id")
limited = False

st.page_link("menu.py", label="Dataset Index", icon="⬅️")

if data_id:
    metadata = pd.read_json('data.json')
    metadata = metadata[metadata['id'] == data_id].to_dict('records')[0]
    st.title(metadata['name'])

    if metadata['data_type'] != 'Dataset':
        st.write(f"The data_type \"{metadata['data_type']}\" is not yet supported for the Explore viewer. Only \"Datasets\" are currently supported. Feature coming soon!")
        st.write(metadata)

    elif metadata['rows'] > 1000000:
        st.write(f"We currently limit loading to datasets that are under 1,000,000 rows. If you'd like to explore this dataset please <a href=\"{metadata['url']}\">visit the dataset page</a> and download your preferred copy and open it locally on your machine.", unsafe_allow_html=True)
        st.write(metadata)

    else:
        df = functions.load_data(data_id)
        print(df.dtypes)
        with st.container(border=True):
            st.text(metadata['description'])
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.subheader(metadata['category'])
                st.caption("Category")

            with col2:
                st.subheader(metadata['views'])
                st.caption("Views")

            with col3:
                st.subheader(metadata['rows'])
                st.caption("Rows")

            with col4:
                st.subheader(metadata['updated'])
                st.caption("Last Updated")


        column_choices = df.columns.values.tolist()

        options = st.multiselect(
            'Select which columns to show. Click the \'x\' at the right to clear all selected columns.',
            column_choices, column_choices)
        st.dataframe(df[options], hide_index=True)

        latitude = None
        longitude = None
        for col in df.columns:
            if functions.is_latitude(df[col]):
                latitude = col
            elif functions.is_longitude(df[col]):
                longitude = col

        if latitude and longitude:
            # drop any na values
            df_coordinates = df.copy().dropna(subset=[latitude, longitude], how='any')
            # drop any rows that have a 0 in the lat or long
            df_coordinates = df_coordinates.loc[~((df_coordinates[latitude].isin([0,1])) | (df_coordinates[longitude].isin([0,1])))]

            # Ensure the data is converted to a list of lists for coordinates
            st.divider()
            st.header("Map")
            # st.map(df_coordinates, longitude=longitude,latitude=latitude, size=1)

            options = df_coordinates.columns
            selection = st.segmented_control(
                "Select data to show on map", options, selection_mode="multi"
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_coordinates,
                get_position=f"[{longitude}, {latitude}]",
                get_radius=100,
                get_color=[255, 0, 0, 140],
                pickable=True,
            )
            # Set the viewport location
            view_state = pdk.ViewState(
                longitude=df_coordinates[longitude].mean(), 
                latitude=df_coordinates[latitude].mean(), 
                zoom=10, 
                min_zoom=6, 
                max_zoom=15, 
                pitch=0, 
                bearing=0
            )

            tooltip_html = "<div style='max-width:250px'>" + "".join([f"<p>{{{s}}}</p>" for s in selection]) + "</div>"

            # Combined all of it and render a viewport
            r = pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"html": tooltip_html, "style": {"color": "white"}},
            )
            st.pydeck_chart(r, height=600)
            
        
        st.header("Pivot Table")
        value_selected = None
        grouping_selected = None
        aggregation_type = 'count'
        grouping_selected = st.pills('Grouping column...  *Required', df.columns, key='pivot_group_select')
        column_selected = st.pills('Pivot columns... (optional)', df.columns, key='pivot_column_select')
        value_selected = st.pills('Value column...  *Required', df.columns, key='pivot_value_select')

        # will need to figure out how to reliable convert strings to numeric to enable sum and mean
        # aggregation_type = st.pills('Aggregation type...', ['count', 'sum', 'mean', 'min', 'max'])
        # aggfunc_map = {
        #     'count': 'count',
        #     'sum': np.sum,
        #     'mean': np.mean,
        #     'min': np.min,
        #     'max': np.max
        # }

        if value_selected and grouping_selected:
            pivot_table = pd.pivot_table(df, values=value_selected, index=grouping_selected, columns=column_selected, aggfunc='count')
            st.dataframe(pivot_table, use_container_width=True)



else:
    st.warning('No dataset selected. Please go back.')
    df = None






