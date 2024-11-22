import pandas as pd

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

    # do not process lat or long columns
    if is_latitude(series):
        return pd.Series(dtype=str)
    
    elif is_longitude(series):
        return pd.Series(dtype=str)
    
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