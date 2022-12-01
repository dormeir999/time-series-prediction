from itertools import product
from functools import reduce # Valid in Python 2.6+, required in Python 3
import operator
import sys

def print_func_name():
    the_name = sys._getframe(1).f_code.co_name
    return print(f'{the_name}()')

def get_features_time_dependence(the_df):
    print_func_name()
    is_fixed_features_df = (the_df.groupby(index_cols)[features_orig].nunique(dropna=False) == 1).all()
    the_time_fixed_features = is_fixed_features_df[is_fixed_features_df==True].index
    the_time_variant_features = is_fixed_features_df[is_fixed_features_df==False].index
    return the_time_fixed_features, the_time_variant_features

def move_cols_to_first(the_df, first_cols: list):
    print_func_name()
    latter_cols = the_df.columns[~the_df.columns.isin(first_cols)]
    the_df = pd.concat([the_df[first_cols], the_df[latter_cols]],axis=1)
    return the_df

def add_indexes_col(the_df, indicator=False):
    print_func_name()
    indexes_col = "_".join(index_cols)
    the_df = the_df.copy(deep=True)
    the_df[indexes_col] = the_df[index_cols[0]].astype(str)
    if len(indexes_col)>1:
        for col in index_cols[1:]:
            the_df[indexes_col] = the_df[indexes_col].astype(str) + "_" + the_df[col].astype(str)
    if time_col in the_df:
        the_df = move_cols_to_first(the_df, [time_col,indexes_col]+index_cols)
    else:
        the_df = move_cols_to_first(the_df, [indexes_col]+index_cols)
    return the_df, indexes_col

def is_full_time_df(the_df):
    print_func_name()
    is_full_time = len(the_df) == reduce(operator.mul, the_df[index_cols+[time_col]].nunique())
    return is_full_time

def is_target_clean(the_df):
    print_func_name()
    return the_df[target].isna().sum() == 0

def target_fillna(the_df):
    """ To be used when NA is a fixed default value, like 0"""
    print_func_name()
    assert target in the_df
    the_df[target] = the_df[target].fillna(target_fillna_value)
    assert is_target_clean(the_df)
    return the_df

def target_dropna(the_df):
    print_func_name()
    the_df = the_df.dropna(subset=[target])
    assert the_df[target].isna().sum() == 0

def target_fix_na(the_df):
    print_func_name()
    if target_na_decision=='fill':
        the_df = target_fillna(the_df)
    elif target_na_decision=='drop':
        the_df = target_dropna(the_df)
    return the_df

def is_index_cols_clean(the_df):
    print_func_name()
    return (the_df[index_cols].isna().sum()==0).all()

def recreate_index_cols_from_indexes_col(the_df):
    "recreate the original index cols that are missing for the dates that were missing"
    if is_index_cols_clean(the_df):
        return the_df
    assert indexes_col in the_df
    recreated_index_values = the_df[the_df[index_cols].isna().any(axis=1)][indexes_col].str.split('_', expand=True)
    recreated_index_values.columns=index_cols
    the_df.loc[the_df[index_cols].isna().any(axis=1), index_cols] = recreated_index_values
    assert is_index_cols_clean(the_df)
    return the_df


def time_fixed_features_fillna(the_df):
    print_func_name()
    # Make sure there's one index col
    the_indexes_col = "_".join(index_cols)
    if not the_indexes_col in the_df:
        the_df, the_indexes_col = add_indexes_col(the_df)
    time_fixed_features_values_per_index = the_df.dropna(subset=time_fixed_features).groupby(the_indexes_col)[time_fixed_features].last().reset_index()
    # Make index_cols of time_fixed_features_values_per_index same type as the_df
    #time_fixed_features_values_per_index[index_cols] = time_fixed_features_values_per_index[index_cols].astype(the_df[index_cols].dtypes.drop_duplicates()[0])
    the_df = the_df.drop(columns=time_fixed_features)
    #return the_df, time_fixed_features_values_per_index
    the_df = the_df.merge(time_fixed_features_values_per_index, on=the_indexes_col, how='left')
    return the_df

def add_missing_dates_fill_target_zero(the_df):
    print_func_name()
    if is_full_time_df(the_df):
        return the_df
    # Make sure there's one index col
    the_indexes_col = "_".join(index_cols)
    if not the_indexes_col in the_df:
        the_df, the_indexes_col = add_indexes_col(the_df)
    # The logic
    the_df_full_date_indexes = pd.DataFrame(product(the_df[time_col].drop_duplicates(), the_df[the_indexes_col].drop_duplicates()), columns=[time_col, the_indexes_col]).dropna()
    the_df = the_df.merge(the_df_full_date_indexes, how='right')
    ## fillna's
    the_df = recreate_index_cols_from_indexes_col(the_df)
    #return the_df
    the_df = time_fixed_features_fillna(the_df)
    the_df = target_fillna(the_df)
    return the_df
    assert is_full_time_df(the_df)
    return the_df
