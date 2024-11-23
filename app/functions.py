import pandas as pd
import streamlit as st
import requests

def is_latitude(series):
    try:
        min_val = series.astype(float).loc[~series.isin([0,1])].min()
        max_val = series.astype(float).loc[~series.isin([0,1])].max()

        if min_val > 40 and max_val < 41:
            return True
        else:
            return False
    except Exception:
        return False
    

def is_longitude(series):
    try:
        min_val = series.astype(float).loc[~series.isin([0,1])].min()
        max_val = series.astype(float).loc[~series.isin([0,1])].max()

        if min_val > -74.5 and max_val < -73.5:
            return True
        else:
            return False
    except Exception:
        return False


def convert_column_to_date(series):
    
    try:
            
        # look for date columns and convert
        converted_col = pd.to_datetime(series, errors='coerce')
        
        if converted_col.isna().all():
            return pd.Series(dtype=str)

        # Check if the column might be just years
        potential_years = series.str.match(r'^\d{4}$')
        if potential_years.all():
            # df[col] = series.astype(int)
            return series
        
        # Check if we have any time components
        has_time = False
        non_nat_mask = ~converted_col.isna()
        if non_nat_mask.any():
            times = converted_col[non_nat_mask].dt.time
            has_time = not (times == pd.Timestamp('00:00:00').time()).all()
        
        if has_time:
            # Keep as full datetime if there are time components
            return converted_col
        else:
            # Convert to date only if no time components
            return converted_col.dt.date
            
    except (ValueError, TypeError):
        return pd.Series(dtype=str)
    

def convert_column_to_numeric(series):
    try:
        converted_col = pd.to_numeric(series, errors='raise')
        return converted_col
        
    except Exception:
        return pd.Series(dtype=str)
    

@st.cache_data()
def load_data(data_id):
    '''
    Takes in a data_id and pings the API to retieve the data. Converts numeric columns using 
    to_numeric, and then date columns using to_datetime
    '''
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
        if offset > 100000:
            break

    df = pd.DataFrame.from_dict(data_rows)
    df.dropna(how='all', inplace=True)
    # go through each column, process, and look for data types
    for col in df.columns:
        # Skip non-string columns
        if df[col].dtype != 'object':
            continue
        
        # Remove any leading/trailing whitespace
        series = df[col].str.strip()

        # check if the column is numeric, and convert
        # do this first, before datetime, because the datetime will try to convert some numbers
        # but to_numeric will not pick up datetimes
        converted_col = convert_column_to_numeric(series)
        if not converted_col.empty:
            df[col] = converted_col
            continue

        # check if the column is datetime and convert
        converted_col = convert_column_to_date(series)
        if not converted_col.empty:
            df[col] = converted_col
            continue

    df_coordinates = df.copy()
    
    return df, df_coordinates