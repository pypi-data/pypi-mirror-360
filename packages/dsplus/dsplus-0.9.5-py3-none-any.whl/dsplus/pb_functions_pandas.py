#region Libraries

#%%
from typing import Literal, Any
from tqdm import tqdm

import pandas as pd
import numpy as np

pd.options.display.max_columns = None
pd.options.display.max_rows = 8

#endregion -----------------------------------------------------------------------------------------
#region Functions: Set Operations

#%%
def set_union_series(*v) -> pd.Series:
    '''Get the union of all elements in vectors. Alternative to 'set_union'.

    Args:
        *v (list | np.ndarray | pd.Series): Multiple vectors.

    Returns:
        pd.Series: Resulting series.

    Examples:
        >>> set_union_series(v1, v2, v3)
    '''
    # element1 = v[0]
    # v1 = vector_to_series(element1)
    # for element2 in v[1:]:
    #     v2 = vector_to_series(element2)

    #     v1 = pd_concat_series(v1, v2)

    # return v1

    result = pd.concat([pd.Series(vector) for vector in v], ignore_index=True).drop_duplicates()

    return result


#%%
def set_union(*v) -> np.ndarray:
    '''Get the union of all elements in vectors. Alternative to 'set_union_series'.

    Args:
        *v (list | np.ndarray | pd.Series): Multiple vectors.

    Returns:
        np.ndarray: Resulting array.

    Examples:
        >>> set_union(v1, v2, v3)
    '''
    return set_union_series(*v).to_numpy()

#%%
def set_intersection_series(*v) -> pd.Series:
    '''Get common elements in vectors. Alternative to 'set_intersection'.

    Args:
        *v (list | np.ndarray | pd.Series): Multiple vectors.

    Returns:
        pd.Series: Resulting series.

    Examples:
        >>> set_intersection_series(v1, v2, v3)
    '''
    element1 = v[0]
    v1 = pd_to_series(element1)
    for element2 in v[1:]:
        v2 = pd_to_series(element2)

        v1 = v1[v1.isin(v2)]

    return v1

#%%
def set_intersection(*v) -> np.ndarray:
    '''Get common elements in vectors. Alternative to 'set_intersection_series'.

    Args:
        *v (list | np.ndarray | pd.Series): Multiple vectors.

    Returns:
        np.ndarray: Resulting array.

    Examples:
        >>> set_intersection(v1, v2, v3)
    '''
    return set_intersection_series(*v).to_numpy()

#%%
def set_diff_series(v1: list|np.ndarray|pd.Series, v2: list|np.ndarray|pd.Series) -> pd.Series:
    '''Get elements in 'v1' that are not in 'v2'. Alternative to 'set_diff'.

    Args:
        v1 (list | np.ndarray | pd.Series): First vector.
        v2 (list | np.ndarray | pd.Series): Second vector.

    Returns:
        pd.Series: Resulting series.
    '''
    v1 = pd_to_series(v1)
    v2 = pd_to_series(v2)

    return v1[~v1.isin(v2)]

#%%
def set_diff(v1: list|np.ndarray|pd.Series, v2: list|np.ndarray|pd.Series) -> np.ndarray:
    '''Get elements in 'v1' that are not in 'v2'. Alternative to 'set_diff_series'.

    Args:
        v1 (list | np.ndarray | pd.Series): First vector.
        v2 (list | np.ndarray | pd.Series): Second vector.

    Returns:
        np.ndarray: Resulting array.
    '''
    return set_diff_series(v1, v2).to_numpy()

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Type Conversion

#%%
def pd_to_series(vector: str|list|np.ndarray|pd.Series) -> pd.Series:
    '''Convert different types of vectors to series.

    Args:
        vector (str | list | np.ndarray | pd.Series): Vector.

    Returns:
        pd.Series: Converted series. If unrecognized type is passed, np.nan is returned.

    Examples:
        >>> pd_to_series('a')
        >>> pd_to_series([1, 2, 3])
    '''
    if isinstance(vector, str):
        vector = pd.Series([vector])
    elif pd.api.types.is_number(vector):
        vector = pd.Series([vector])
    elif isinstance(vector, list):
        vector = pd.Series(vector)
    elif isinstance(vector, np.ndarray):
        vector = pd.Series(vector)
    elif isinstance(vector, pd.Series):
        pass
    elif isinstance(vector, pd.core.indexes.base.Index):
        vector = vector.to_series()
    else:
        vector = pd.Series() #np.nan

    return vector

#%%
def pd_to_numpy(vector: str|list|np.ndarray|pd.Series) -> np.ndarray:
    '''Convert different types of vectors to array.

    Args:
        vector (str | list | np.ndarray | pd.Series): Vector.

    Returns:
        np.ndarray: Converted array. If unrecognized type is passed, np.nan is returned.

    Examples:
        >>> pd_to_numpy('a')
        >>> pd_to_numpy([1, 2, 3])
    '''
    # if isinstance(vector, str):
    #     vector = np.array([vector])
    # elif isinstance(vector, list):
    #     vector = np.array(vector)
    # elif isinstance(vector, np.ndarray):
    #     pass
    # elif isinstance(vector, pd.Series):
    #     vector = vector.to_numpy()
    # elif isinstance(vector, pd.core.indexes.base.Index):
    #     vector = vector.to_series().to_numpy()
    # else:
    #     vector = np.array() #np.nan
    vector = pd_to_series(vector).to_numpy()

    return vector

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Slice

#%%
def pd_cols(df: pd.DataFrame, cols: str, return_series=False) -> np.ndarray|pd.Series:
    '''Get a vector of desired column names in desired order.

    Args:
        df (pd.DataFrame): Dataframe whose column names are to be extracted.
        cols (str): String representing column name extraction rules. See notes.
        return_series (bool, optional): Whether to return an array or series of column names. Defaults to False (return series).

    Returns:
        np.ndarray | pd.Series: Array or series of column names.

    Notes:
        - 'cols' is comprised of individual pieces separated by comma.
            - Whitespaces before and after comma are ignored.
        - Each piece can be a column name, a slice, a pandas string function, or an asterisk (*).
        - Slice means a two column names separated by a colon. eg. 'v1:v5' means all columns from 'v1' to 'v5' (inclusive).
            - If the first columnn name is omitted, it means everything before. For eg. ':v5' means all column upto and including 'v5'.
            - If the last column name is omitted, it means everything after. For eg. 'v1:' means all column anmes from and including 'v1'.
        - To specify pandas string function, the piece should start with 'str.'. For eg. 'str.startswith("v2")'.
            - The function should return True or False values on all columns of 'df'.
        - To specify data type, the piece should start with 'select_dtypes('. For eg. 'select_dtypes("category")'.
        - An asterisk (*) means all other columnn names.
            - All other column except for all other inclusions and exclusions (before or after the asterisk) will be placed in place of the asterisk (*).
        - Any piece can be negated adding a '-' in front. These columns are excluded. Examples:
            - '-v1' means exclude column 'v1'.
            - '-v1:v5' means exclude columns from 'v1' to 'v5' (inclusive).
            - '-:v5' means exclude all columns upto and including 'v5'.
            - '-v1:' means exclude all columns from and including 'v1'.
        - If any columns to keep are repeated, only the first occurence is kept.
        - Any columns to be excluded will be excluded. Exclusion takes precedence over inclusion.
        - If no inclusions are provided, all columns are taken as inclusions.
            - This is useful when only exclusions are provided.

    Examples:
        >>> df = pd.DataFrame(columns = ['v'+str(_) for _ in range(21)]).astype(dict(v5=int, v15=int, v0='category'))
        >>> pd_cols(df, ':v2, v4:v6, *, v9:v10, -v12:v13, -v11, -v17:')
        >>> pd_cols(df, 'v1:v2, v4:v6, *, v9:v10')
        >>> pd_cols(df, 'v4:')
        >>> pd_cols(df, ':v9, -v2')
        >>> pd_cols(df, 'v9:, -v12')
        >>> pd_cols(df, '*, -v12, -v4:v9')
        >>> pd_cols(df, 'v15:, *')
        >>> pd_cols(df, 'str.contains("v2"), *, -str.startswith("v1"), -v8')
        >>> pd_cols(df, '-select_dtypes("category")')
        >>> pd_cols(df, 'select_dtypes("number"), *')
        >>> pd_cols(df, '-v2:')
        >>> df[lambda _: pd_cols(_, 'v15:, *')]
    '''
    v_cols_all = df.columns.to_series()

    cols_split = [_.strip() for _ in cols.split(',')]

    v_cols = pd.Series()
    v_cols_drop = pd.Series()

    for col in cols_split:
        if col=='*':
            temp_v_cols = ['*']
        elif col[0:4] == 'str.':
            temp_v_cols = eval('df.columns[df.columns.' + col + ']').tolist()
        elif col[0:5] == '-str.':
            temp_v_cols = eval('df.columns[df.columns.' + col[1:] + ']').tolist()
        elif col[0:14] == 'select_dtypes(':
            temp_v_cols = eval('df.' + col + '.columns.tolist()')
        elif col[0:15] == '-select_dtypes(':
            temp_v_cols = eval('df.' + col[1:] + '.columns.tolist()')
        elif ':' in col:
            temp_v_cols = [_.strip().replace('-', '') for _ in col.split(':')]
            if temp_v_cols[0] == '':
                index_from = 0
            else:
                index_from = v_cols_all.tolist().index(temp_v_cols[0])
            if temp_v_cols[1] == '':
                index_to = len(v_cols_all)
            else:
                index_to = v_cols_all.tolist().index(temp_v_cols[1])
            temp_v_cols = v_cols_all[index_from:index_to+1]
        else:
            temp_v_cols = [col.replace('-', '')]

        if col[0] == '-':
            v_cols_drop = set_union_series(v_cols_drop, temp_v_cols)
        else:
            v_cols = set_union_series(v_cols, temp_v_cols)

    if v_cols.isin(['*']).any():
        index_everything = v_cols.to_list().index('*')
        v_everything = set_diff_series(v_cols_all, v_cols)

        v_cols = pd.concat([v_cols.iloc[:index_everything],
                            v_everything,
                            v_cols.iloc[index_everything+1:]])

    if v_cols.size == 0:
        v_cols = v_cols_all.copy()

    v_cols = set_diff_series(v_cols, v_cols_drop)

    if not return_series:
        v_cols = v_cols.to_numpy()
    else:
        v_cols = v_cols.reset_index(drop=True)

    return v_cols

#%%
def pd_select(df: pd.DataFrame, cols: str) -> pd.DataFrame:
    '''Keep desired columns in desired order. Uses 'pd_cols()' as a backend.

    Args:
        df (pd.DataFrame): Dataframe whose column names are to be selected.
        cols (str): String representing column name selection rules. See notes.

    Returns:
        pd.DataFrame: Dataframe with selected columns in desired order.

    Notes (taken directly from 'pd_cols()'):
        - 'cols' is comprised of individual pieces separated by comma.
            - Whitespaces before and after comma are ignored.
        - Each piece can be a column name, a slice, a pandas string function, or an asterisk (*).
        - Slice means a two column names separated by a colon. eg. 'v1:v5' means all columns from 'v1' to 'v5' (inclusive).
            - If the first columnn name is omitted, it means everything before. For eg. ':v5' means all column upto and including 'v5'.
            - If the last column name is omitted, it means everything after. For eg. 'v1:' means all column anmes from and including 'v1'.
        - To specify pandas string function, the piece should start with 'str.'. For eg. 'str.startswith("v2")'.
            - The function should return True or False values on all columns of 'df'.
        - To specify data type, the piece should start with 'select_dtypes('. For eg. 'select_dtypes("category")'.
        - An asterisk (*) means all other columnn names.
            - All other column except for all other inclusions and exclusions (before or after the asterisk) will be placed in place of the asterisk (*).
        - Any piece can be negated adding a '-' in front. These columns are excluded. Examples:
            - '-v1' means exclude column 'v1'.
            - '-v1:v5' means exclude columns from 'v1' to 'v5' (inclusive).
            - '-:v5' means exclude all columns upto and including 'v5'.
            - '-v1:' means exclude all columns from and including 'v1'.
        - If any columns to keep are repeated, only the first occurence is kept.
        - Any columns to be excluded will be excluded. Exclusion takes precedence over inclusion.
        - If no inclusions are provided, all columns are taken as inclusions.
            - This is useful when only exclusions are provided.

    Examples:
        >>> df = pd.DataFrame(columns = ['v'+str(_) for _ in range(21)]).astype(dict(v5=int, v15=int, v0='category'))
        >>> df.pipe(pd_select, ':v2, v4:v6, *, v9:v10, -v12:v13, -v11, -v17:')
        >>> df.pipe(pd_select, 'v1:v2, v4:v6, *, v9:v10')
        >>> df.pipe(pd_select, 'v4:')
        >>> df.pipe(pd_select, ':v9, -v2')
        >>> df.pipe(pd_select, 'v9:, -v12')
        >>> df.pipe(pd_select, '*, -v12, -v4:v9')
        >>> df.pipe(pd_select, 'v15:, *')
        >>> df.pipe(pd_select, 'str.startswith("v2"), *')
        >>> df.pipe(pd_select, 'str.contains("v2"), *, -str.startswith("v1"), -v8')
        >>> df.pipe(pd_select, '-select_dtypes("category")')
        >>> df.pipe(pd_select, 'select_dtypes("number"), *')
        >>> df.pipe(pd_select, '-v2:')
    '''
    return df[lambda _: pd_cols(_, cols)]

#%%
def pd_drop_rows(df: pd.DataFrame, rows: int|list|np.ndarray|pd.Series) -> pd.DataFrame:
    '''Drops row(s) from dataframe.

    Args:
        df (pd.DataFrame): Dataframe.
        rows (int | list | np.ndarray | pd.Series): Row location or vector of row locations to drop.

    Returns:
        pd.DataFrame: Dataframe with row(s) dropped.

    Examples:
        >>> pd_drop_rows(df, 5)
        >>> pd_drop_rows(df, [5, 6])
    '''
    rows = pd_to_series(rows)

    df = df[~np.isin(np.arange(df.shape[0]), rows)]

    return df

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Concat

#%%
def pd_concat_series(v_values: pd.Series, values: float|list|np.ndarray|pd.Series) -> pd.Series:
    '''Append values to series.

    Args:
        v_values (Series): Series.
        values (float | list | np.ndarray | pd.Series): Vector of values to append.

    Returns:
        pd.Series: Concatenated series.

    Examples:
        >>> v_values = pd.Series([0,1,2])
        >>> pd_concat_series(v_values, 3)
        >>> pd_concat_series(v_values, [3, 4])
        >>> v_values.pipe(pd_concat_series, 3)
        >>> v_values.pipe(pd_concat_series, [3, 4])
    '''
    v_values_concat = pd.concat([v_values, pd.Series(values)])
    return v_values_concat

#%%
def pd_concat_rows(df1: pd.DataFrame, df2: pd.DataFrame, ignore_index = True) -> pd.DataFrame:
    '''Concatenate dataframes by rows. Mainly useful for piping with 'pd.pipe()'. Wrapper around 'pd.concat()'. If one of the dataframes is blank, the other is returned, ensuring no change in datatype like with 'pd.concat()'.

    Args:
        df1 (pd.DataFrame): Dataframe.
        df2 (pd.DataFrame): Dataframe.
        ignore_index (bool):  If True, do not use the index values along the concatenation axis. The resulting axis will be labeled 0, ..., n - 1. Defaults to True.

    Returns:
        pd.DataFrame: Concatenated dataframe.

    Examples:
        >>> pd_concat_rows(df1, df2)
        >>> df1.pipe(pd_concat_rows, df2)
    '''
    if df1.shape[0] == 0:
        return df2
    if df2.shape[0] == 0:
        return df1
    return pd.concat([df1, df2], axis=0, ignore_index=ignore_index)

#%%
def pd_concat_rows_multiple(*l_df) -> pd.DataFrame:
    '''Concatenate multiple dataframes by rows. Wrapper around 'pd_concat_rows()'.

    Args:
        *l_df: Dataframes.

    Returns:
        pd.DataFrame: Concatenated dataframe.

    Examples:
        >>> pd_concat_rows_multiple(df1, df2, df3)
        >>> df1.pipe(pd_concat_rows, df2, df3)
    '''
    df = pd.DataFrame()
    for df2 in l_df:
        df = df.pipe(pd_concat_rows, df2)

    return df

#%%
def pd_concat_cols(df1: pd.DataFrame,
                   df2: pd.DataFrame,
                   ignore_index = True,
                   drop_index = True) -> pd.DataFrame:
    '''Concatenate dataframes by columns. Mainly useful for piping with 'pd.pipe()'. Wrapper around 'pd.concat()'.

    Args:
        df1 (pd.DataFrame): Dataframe.
        df2 (pd.DataFrame): Dataframe.
        ignore_index (bool): Reset index for the two dataframes. Defaults to True.
        drop_index (bool): Drop the index when resetting index. Defaults to True.

    Returns:
        pd.DataFrame: Concatenated dataframe.

    Examples
        >>> pd_concat_cols(df1, df2)
        >>> df1.pipe(pd_concat_cols, df2)
    '''
    if ignore_index:
        return pd.concat([df1.reset_index(drop=drop_index),
                          df2.reset_index(drop=drop_index)],
                         axis=1)

    return pd.concat([df1, df2], axis=1)

#%%
def pd_concat_cols_multiple(*l_df) -> pd.DataFrame:
    '''Concatenate multiple dataframes by cols. Wrapper around 'pd_concat_cols()' with 'ignore_index' and 'drop_index' set to True.

    Args:
        *l_df: Dataframes.

    Returns:
        pd.DataFrame: Concatenated dataframe.

    Examples:
        >>> pd_concat_rows_multiple(df1, df2, df3)
        >>> df1.pipe(pd_concat_rows, df2, df3)
    '''
    df = pd.DataFrame()
    for df2 in l_df:
        df = df.pipe(pd_concat_cols, df2)

    return df

#%%
def pd_add_row(df: pd.DataFrame, row: list|np.ndarray|pd.Series) -> pd.DataFrame:
    '''Add a vector as a row to a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to add a row.
        row (pd.Series): Row to add to the DataFrame.

    Returns:
        pd.DataFrame: DataFrame with the added row.

    Examples:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y']})
        >>> df.pipe(pd_add_row, [3, 'z'])
    '''
    df = df.copy()
    df.loc[len(df)] = row

    return df

#%%
def pd_repeat_rows(df: pd.DataFrame, n: int) -> pd.DataFrame:
    '''Repeats a row of a single row dataframe.

    Args:
        df (pd.DataFrame): Dataframe with one row.
        n (int): Number of times to repeat the rows.

    Returns:
        pd.DataFrame: Dataframe with row repeated.

    Examples:
        >>> pd_repeat_rows(df, 5)
    '''
    return pd.concat([df]*n, ignore_index=True)

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Merge

#%%
def pd_merge_asof(df1: pd.DataFrame,
                  df2: pd.DataFrame,
                  on: str = None,
                  left_on: str = None,
                  right_on: str = None,
                  direction: Literal['backward', 'forward', 'nearest'] = 'forward',
                  one_to_many = False) -> pd.DataFrame:
    '''Perform a merge by key direction. Wrapper around 'pandas.merge_asof()'. Unlike 'pandas.merge_asof()', default direction is 'forward'. Additionally, 'one_to_many' is an additional option. Finally, if one of the two dataframes are blank, 'df1' is still returned along with columns from 'df2' added and set to np.nan, and no error is raised

    Args:
        df1 (pd.DataFrame): Dataframe.
        df2 (pd.DataFrame): Dataframe.
        on (str, optional): Common column name from 'df1' and 'df2' to join on. Defaults to None.
        left_on (str, optional): Column name from 'df1' to be joined on. Defaults to None.
        right_on (str, optional): Column name from 'df2' to be joined on. Defaults to None.
        direction (str, optional): Whether to search for prior, subsequent, or closest matches. Defaults to 'forward'. Acceptable values: 'forward', 'backward', or 'closest'.
        one_to_many (bool, optional): Whether to join one-to-one or one-to-many. Defaults to False (i.e. perform one-to-one join, default behavior of 'pandas.merge_asof()').

    Returns:
        pd.DataFrame: Merged Dataframe.

    Notes:
        - Either 'on' or both of 'left_on' and 'right_on' needs to be specified.
        - If 'one_to_many' is False, a value from 'df2' is only matched once with a value (closest) from 'df2'.
        - If 'one_to_many' is True, a value from 'df2' is matched multiple times with values from 'df1' until there is another match.
    '''
    if on is not None:
        left_on = on
        right_on = on
    if (df1.shape[0] > 1) & (df2.shape[0] > 0):
        if one_to_many:
            direction_rev = np.select(direction == np.array(['forward', 'backward', 'nearest']),
                                    ['backward', 'forward', 'nearest'],
                                    'backward').item()
            temp_df = pd.merge_asof(left = df2,
                                    right = df1.loc[:, [left_on]].eval(left_on + '_new = ' + left_on),
                                    left_on = right_on,
                                    right_on = left_on,
                                    direction = direction_rev).pipe(pd_drop, left_on)
            df = df1.merge(temp_df,
                           left_on = left_on,
                           right_on = left_on + '_new',
                           how = 'left').pipe(pd_drop, left_on + '_new')
        else:
            df = pd.merge_asof(left = df1,
                               right = df2,
                               left_on = left_on,
                               right_on = right_on,
                               direction = direction)
    else:
        df = df1
        df2 = df2.drop(right_on, axis=1)
        for col_name in df2.columns.to_series():
            df = df.assign(**{col_name: np.nan})

    return df

def pd_merge_between_indices(df1: pd.DataFrame,
                             df2: pd.DataFrame,
                             left_min_col: str,
                             left_max_col :str,
                             right_col: str) -> pd.DataFrame:
    '''Merge two dataframe where a value in column, 'right_col', in 'df2' has to be between two columns, 'left_min_col' and 'left_max_col', in 'df1'.

    Args:
        df1 (pd.DataFrame): Dataframe.
        df2 (pd.DataFrame): Dataframe.
        left_min_col (str): Numeric column in 'df1' indicating lower limit for 'right_col'.
        left_max_col (str): Numeric column in 'df1' indicating upper limit for 'right_col'.
        right_col (str): Numeric column in 'df2'.

    Returns:
        pd.DataFrame: Joined dataframe.
    '''
    if (df1.shape[0] > 1) and (df2.shape[0] > 0):
        temp_df = \
            (df1
                .loc[:, [left_min_col, left_max_col]]
                .pipe(pd_merge_asof,
                      df2,
                      left_on = left_min_col,
                      right_on = right_col,
                      one_to_many=True)
                .loc[lambda _: _[left_max_col] >= _[right_col]]
                .pipe(pd_drop, [left_max_col])
            )
        df = df1.merge(temp_df, how='left', on=left_min_col)
    else:
        df = df1

    return df

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Reshape

#%%
def pd_pivot_longer(df_wide: pd.DataFrame,
                    id_vars: str|list|np.ndarray|pd.Series,
                    value_vars: str|list|np.ndarray|pd.Series = None,
                    var_name: str = None,
                    value_name: str = None) -> pd.DataFrame:
    '''Reshape table from wide to long. Wrapper around 'pd.melt()' but provides easier documentation.

    Args:
        df_wide (pd.DataFrame): Dataframe in wide format.
        id_vars (str | list | np.ndarray | pd.Series): Columns that uniquely identify each observation.
        value_vars (str | list | np.ndarray | pd.Series, optional): Columns to unpivot. Defaults to None. If set to None, all of the other columns are used.
        var_name (str, optional): Name to use for the 'variable' column. Defaults to None. If set to None, new column is named 'variable'.
        value_name (str, optional): Name to use for the 'value' column. Defaults to None. If set to None, new column is named 'value'.

    Returns:
        pd.DataFrame: Dataframe in long format.

    Examples:
        >>> df_wide.pipe(pd_pivot_longer, id_vars='type1')
        >>> df_wide.pipe(pd_pivot_longer, id_vars='type1', var_name='type2', value_name='value1')
        >>> df_wide.pipe(pd_pivot_longer,
                         id_vars='type1',
                         value_vars=['t1', 't2'],
                         var_name='type2',
                         value_name='value1')
    '''
    if value_name is not None:
        df_long = df_wide.melt(id_vars=id_vars,
                               value_vars=value_vars,
                               var_name=var_name,
                               value_name=value_name)
    else:
        df_long = df_wide.melt(id_vars=id_vars,
                               value_vars=value_vars,
                               var_name=var_name)

    return df_long

#%%
def pd_pivot_wider(df_long: pd.DataFrame,
                   index: str|list|np.ndarray|pd.Series,
                   columns: str,
                   values: str|list|np.ndarray|pd.Series = None,
                   keep_val:bool = False,
                   join_sep: str = '_',
                   col_first:bool = True) -> pd.DataFrame:
    '''Reshape table from long to wide. Wrapper around 'pd.pivot()' but prevents multiindex and provides easier documentation.

    Args:
        df_long (pd.DataFrame): Dataframe in long format.
        index (str | list | np.ndarray | pd.Series): Columns that uniquely identify each observation.
        columns (str): Column to get names from.
        values (str | list | np.ndarray | pd.Series, optional): Column to get values from. Defaults to None. If set to None, all remaining columns are used.
        keep_val (bool, optional): See notes. Defaults to False.
        join_sep (str, optional): See notes. Defaults to '_'.
        col_first (bool, optional): See notes. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe in wide format.

    Notes:
        - If there is a single 'values' column and 'keep_val' is False, widened column names are taken from values in 'columns'.
        - If 'keep_val' is True or if there are multiple 'values' column, values in 'columns' column is joined with column names provided in 'values', separated by 'join_sep'. Values in 'columns' column precede if 'col_first' is True.

    Examples:
        >>> df_long.pipe(pd_pivot_wider, index='type1', columns='type2')
        >>> df_long2.pipe(pd_pivot_wider,
                          index=['type1', 'type1_'],
                          columns='type2',
                          values=['value1', 'value2'],
                          join_sep='__',
                          col_first=False)
    '''
    if values is None:
        columns_all = df_long.columns.to_series()
        values = columns_all[~columns_all.isin(pd_to_series(index))][columns_all != columns]

    values = pd_to_series(values)

    if len(values) == 1 and not keep_val:
        values = values.iloc[0]

    df_wide = df_long.pivot(index=index, columns = columns, values = values)

    df_wide = \
        (df_wide
            .pipe(pd_reset_column, rev=col_first, join_sep=join_sep)
            .reset_index()
        )

    return df_wide

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Conditionals

#%%
def pd_if_else(condition: bool|list|np.ndarray|pd.Series, v_true: Any|list|np.ndarray|pd.Series, v_false: Any|list|np.ndarray|pd.Series) -> Any | np.ndarray:
    '''If-else statement. Wrapper around 'np.where()'. Returns either single value or array instead of array.

    Args:
        condition (bool | list | np.ndarray | pd.Series): Vector of conditions.
        v_true (Any | list | np.ndarray | pd.Series): Vector of values if condition is true.
        v_false (Any | list | np.ndarray | pd.Series): Vector of values if condition is false.

    Returns:
        Any | np.ndarray: Resulting vector. If condition is 'condition' is bool, single value is returned, otherwise Array is returned.

    Notes:
        - Use 'pd_if_else_series()' to get output as series.
        - 'pd_if_else()' is preferred since it does not cause index conflict during dataframe assignment.

    Examples:
        >>> pd_if_else(5 > 6, 5, 6)
        >>> pd_if_else(v < 0, 0, v)
    '''
    result = np.where(condition, v_true, v_false)

    if isinstance(condition, bool):
        result = result.tolist()

    return result

#%%
np_if_else = pd_if_else

#%%
def pd_if_else_series(condition: bool|list|np.ndarray|pd.Series, v_true: Any|list|np.ndarray|pd.Series, v_false: Any|list|np.ndarray|pd.Series) -> Any | pd.Series:
    '''If-else statement. Wrapper around 'np.where()'. Returns either single value or Series instead of array.

    Args:
        condition (bool | list | np.ndarray | pd.Series): Vector of conditions.
        v_true (Any | list | np.ndarray | pd.Series): Vector of values if condition is true.
        v_false (Any | list | np.ndarray | pd.Series): Vector of values if condition is false.

    Returns:
        Any | pd.Series: Resulting vector. If condition is 'condition' is bool, single value is returned, otherwise Series is returned.

    Notes:
        - Use 'pd_if_else()' to get output as list.
        - 'pd_if_else()' is preferred since it does not cause index conflict during dataframe assignment.

    Examples:
        >>> pd_if_else(5 > 6, 5, 6)
        >>> pd_if_else(v < 0, 0, v)
    '''
    result = np.where(condition, v_true, v_false)

    if isinstance(condition, bool):
        result = result.tolist()
    else:
        result = pd.Series(result)

    return result

#%%
def pd_case_when(*args) -> np.ndarray:
    '''Vectorized if-else statement. Wrapper around 'np.select()'. Inputs include even number of arguments, each separated by comma in the format: condition1, output1, condition2, output2, ... Final argument can be True, outputn for default output.

    Returns:
        np.ndarray: Resulting array.

    Notes:
        - Use 'pd_case_when_series()' to get output as series.
        - 'pd_case_when()' is preferred since it does not cause index conflict during dataframe assignment.

    Examples:
        >>> df.assign(col_updated = lambda _: pd_case_when(_['col'] > 30, 'Good',
                                                           _['col'] > 20, 'Ok',
                                                           True, _['col']))
    '''
    conditions = args[0::2]
    values = args[1::2]

    result = np.select(conditions, values, values[-1])

    return result

#%%
np_case_when = pd_case_when

#%%
def pd_case_when_series(*args) -> pd.Series:
    '''Vectorized if-else statement. Wrapper around 'np.select()'. Inputs include even number of arguments, each separated by comma in the format: condition1, output1, condition2, output2, ... Final argument can be True, outputn for default output.

    Returns:
        pd.Series: Resulting series.

    Notes:
        - Use 'pd_case_when()' to get output as list.
        - 'pd_case_when()' is preferred since it does not cause index conflict during dataframe assignment.

    Examples:
        >>> df.assign(col_updated = lambda _: pd_case_when_series(_['col'] > 30, 'Good',
                                                                  _['col'] > 20, 'Ok',
                                                                  True, _['col']).reset_index(drop=True))
    '''
    result = pd_case_when(*args)

    result = pd.Series(result)

    return result

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: View

#%%
def pd_style(df: pd.DataFrame,
             negative = True,
             highlight_max = True,
             highlight_min = True,
             precision: int = None):
    '''Return tabular visualization.

    Args:
        df (pd.DataFrame): Dataframe.
        negative (bool, optional): Show negative numbers in red font. Defaults to True.
        max (bool, optional): Highlight max column values in purple. Defaults to True.
        min (bool, optional): Highlight min column vlaues in blue. Defaults to True.
        precision (int, optional): Number of decimals to show. Defaults to None. None means show all decimals.

    Examples:
        >>> df.pipe(style)
    '''
    def _style_negative(v, props=''):
        return props if v < 0 else None
    def _highlight_max(s, props=''):
        return np.where(s == np.nanmax(s.values), props, '')
    def _highlight_min(s, props=''):
        return np.where(s == np.nanmin(s.values), props, '')
    v_col_num = df.select_dtypes('number').columns.to_series()
    df_style = df.style

    if precision is not None:
        df_style = df_style.format(precision = 3)
    if negative:
        df_style = df_style.map(_style_negative,
                                props='color:red;',
                                subset=v_col_num)
    if highlight_max:
        df_style = df_style.apply(_highlight_max,
                                  props='color:white;background-color:blue;',
                                  axis=0,
                                  subset=v_col_num)
    if highlight_min:
        df_style = df_style.apply(_highlight_min,
                                  props='color:white;background-color:purple;',
                                  axis=0,
                                  subset=v_col_num)

    return df_style

#%%
def pd_print(df: pd.DataFrame, title: str = None) -> pd.DataFrame:
    '''Print and return dataframe. This is mainly to be used to print and assign or print and pipe at the same time.

    Args:
        df (pd.DataFrame): Dataframe to print and return.
        title (str, optional): Text to print before printing dataframe. Defaults to None.

    Returns:
        pd.DataFrame: Returns same dataframe as the input.

    Examples:
        >>> df.assign(x = 5).pipe(pd_print).query('y > 5')
    '''
    print ('')
    if title is not None:
        print (title)
    print (df)

    return df

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Index

#%%
def pd_reset_column(df: pd.DataFrame,
                    rev: bool = False,
                    join_sep: str = '_',
                    keep_name: bool = False,
                    join_sep_name: str = '_') -> pd.DataFrame:
    '''Flatten multi-level column and remove column index name.

    Args:
        df (pd.DataFrame): Dataframe.
        rev (bool, optional): Whether to join in reverse order (down to up). Defaults to False.
        join_sep (str, optional): Separator string between column levels when joining. Defaults to '_'.
        keep_name (str, optional): Whether to join column index names to column names. Defaults to False.
        join_sep_name (str, optional): Separator string between column index names and column names when joining. Defaults to '_'.

    Returns:
        pd.DataFrame: Dataframe with single-level column an dno column index name.
    '''
    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df_columns = df.columns.to_list()
        if keep_name:
            df_columns_updated = []
            for i, name in enumerate(df.columns.names):
                if name is not None:
                    for item in df_columns:
                        new_item = list(item)
                        new_item[i] = name + join_sep_name + new_item[i]
                        df_columns_updated.append(tuple(new_item))
            df_columns = df_columns_updated
        if rev:
            df.columns = [join_sep.join(col[::-1]) for col in df_columns]
        else:
            df.columns = [join_sep.join(col) for col in df_columns]
    else:
        if keep_name:
            df.columns = [(df.columns.name + join_sep_name + col) for col in df.columns]
        else:
            df.columns = df.columns.rename(None)

    return df

#%%
def pd_set_colnames(df: pd.DataFrame,
                    col_names: str|list|np.ndarray|pd.Series) -> pd.DataFrame:
    '''Set column names. Wrapper around 'pd.concat()'. Works with length mismatches.

    Args:
        df (pd.DataFrame): Dataframe.
        col_names (str | list | np.ndnp.ndarray | pd.Series): Vector of column names.

    Returns:
        pd.DataFrame: Dataframe with updated column names.

    Notes:
        - If len(col_names) > len(df), additional 'col_names' are excluded.
        - If len(df) > len(col_names), remaning column names are filled with sequence of numbers based on position.

    Examples:
        >>> df = pd.DataFrame({'c1': [1,2],
                               'c2': [3,4]})
        >>> df.pipe(pd_set_colnames, 'c1')
        >>> df.pipe(pd_set_colnames, ['c1', 'c2', 'c3'])
    '''
    col_names = pd_to_series(col_names)

    len_df = df.shape[1]
    len_col_names = len(col_names)

    if len_df > len_col_names:
        col_names = pd.concat([col_names,
                               pd.Series(['_'+str(_) for _ in np.arange(len_col_names, len_df)])],
                              ignore_index=True)
    if len_col_names > len_df:
        col_names = col_names.iloc[:len_df]

    df = df.set_axis(col_names, axis=1)

    return df

#%%
def pd_clean_colnames(df: pd.DataFrame, trailing_underscore=True, clean_names=True, replace_symbols=True, lower=True, clean_duplicates=True, add_attrs=True) -> pd.DataFrame:
    '''Clean dataframe column names.

    Args:
        df (pd.DataFrame): Dataframe whose column names are to be cleaned.
        trailing_underscore (bool, optional): Add a trailing underscore which helps use dot notation. Defaults to True.
        clean_names (bool, optional): If true, spaces, multi-spaces, and multi-underscores are replaced by single underscore and non-underscore symbols are remove or replaced (based on 'replace_symbols'). Defaults to True.
        replace_symbols (bool, optional): If true, replace non-alphanumeric characters (except dashes and underscores) with underscore. If false, remove them. Defaults to True.
        lower (bool, optional): If true, cases for column names are changed to lower. Defaults to True.
        clean_duplicates (bool, optional): If true, duplicate column names are cleaned. The first of the duplicate names is left unchanged, but the rest are suffixed with '_1', '_2' and so on. Defaults to True.
        add_attrs (bool, optional): If true, original column names are saved in attributes under 'col_names_orig' key. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with cleaned column names.

    Notes:
        - Updates made to column names:
            - Underscore is added at the end ('trailing_underscore').
            - Cases are changed to lower ('lower').
            - Leading and trailing whitespaces are removed ('clean_names').
            - Spaces (between other string) and dashes are coverted to underscores ('clean_names').
            - Other non-alphanumeric characters are coverted to underscores or removed  ('clean_names', 'replace_symbols').
            - Multiple consecutive underscores are replaced with single underscore ('clean_names').
            - Duplicate column names are cleaned with suffixes ('clean_duplicates').
    '''
    df = df.copy()

    if add_attrs:
        attrs = dict(col_names_orig = df.columns)

    if lower:
        df.columns = df.columns.str.lower()

    if trailing_underscore:
        df.columns = [f'{x}_' for x in df.columns]

    if clean_names:
        symbol_replacement = '_' if replace_symbols else ''

        df.columns = \
        (df
            .columns
            .str.strip()
            .str.replace(r'\s|-', '_', regex=True)
            .str.replace(r'\W+', symbol_replacement, regex=True)
            .str.replace(r'_+', '_', regex=True)
        )

    # if clean_names:
    #     symbol_replacement = '_' if replace_symbols else ''

    #     df.columns = \
    #     (df
    #         .columns
    #         .str.strip()
    #         .str.replace(r'\s|-', '_', regex=True)
    #         .str.replace(r'\W+', symbol_replacement, regex=True)
    #     )

    # if trailing_underscore:
    #     df.columns = [f'{x}_' for x in df.columns]

    # if clean_names:
    #     df.columns = \
    #     (df
    #         .columns
    #         .str.replace(r'_+', '_', regex=True)
    #     )

    if clean_duplicates:
        _cols = pd.Series(df.columns)

        _col_dup = _cols.value_counts()
        _col_dup = _col_dup[_col_dup > 1]

        if len(_col_dup) > 0:
            print ('Duplicates found:')
            print (_col_dup)

            # for _dup in _cols[_cols.duplicated()].unique():
            #     _cols[_cols[_cols == _dup].index.values.tolist()] = [_dup + '_' + str(i) if i != 0 else _dup for i in range(sum(_cols == _dup))]
            for _dup, _val in _col_dup.items():
                _cols[_cols[_cols == _dup].index] = [f'{_dup}_{i}' if i != 0 else _dup for i in range(_val)]
                # _cols[_cols[_cols == _dup].index.values.tolist()] = [f'{_dup}_{i}' if i != 0 else _dup for i in range(_val)]

            df.columns = _cols

    if add_attrs:
        df.attrs = attrs

    return (df)

#endregion -----------------------------------------------------------------------------------------
#region Functions: Pandas: Others

#%%
def pd_dataframe(**d) -> pd.DataFrame:
    '''Dataframe definition. Wrapper around 'pd.DataFrame(dict())'.

    Arg:
        **d (dict): Dictionary with column names as keys and column values as values.

    Returns:
        pd.DataFrame: Dataframe.

    Examples:
        >>> pd_dataframe()
        >>> pd_dataframe(x = [1,2,3],
                         y = [5,6,7])
    '''
    return pd.DataFrame(d)

#%%
pd_df = pd_dataframe

#%%
def pd_split_column(df: pd.DataFrame,
                    delim: str,
                    column_original: str,
                    columns_new: list|np.ndarray|pd.Series = None,
                    drop_original = False) -> pd.DataFrame:
    '''Split a column into multiple columns based on deliminator.

    Args:
        df (pd.DataFrame): Dataframe.
        delim (str): Deliminator.
        column_original (str): Name of column to split.
        columns_new (list | np.ndarray | pd.Series, optional): Names of columns after split. Defaults to None.
        drop_original (bool, optional): Whether or not to drop the original column. Defaults to False.

    Returns:
        pd.DataFrame: Dataframe with split columns.

    Examples:
        >>> pd_split_column(df, '_', 'id', ['name', 'type'], drop_original = True)
        >>> df.pipe(lambda _: pd_split_column(_, '_', 'id', ['name', 'type']))
    '''
    # df = df.copy()

    # df[columns_new] = df[column_original].str.split(delim, expand = True)

    df_split = df[column_original].str.split(delim, expand = True)
    if columns_new is not None:
        df_split = df_split.pipe(pd_set_colnames, columns_new)

    df = df.pipe(pd_concat_cols, df_split)

    if drop_original:
        df = pd_drop(df, column_original)

    return df

#%%
def pd_add_row_number(df: pd.DataFrame,
                      col_name: str = 'sn',
                      col_group: str = None,
                      start: int = 0,
                      place_first: bool = True) -> pd.DataFrame:
    '''Add a row number column.

    Args:
        df (pd.DataFrame): Dataframe.
        col_name (str, optional): Name of column to store row numbers. Defaults to 'sn'.
        start (int, optional): Row number for first row. Defaults to 0.
        place_first (bool, optional): Place row number column at the start. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with new row number column.

    Examples:
        >>> df.pipe(pd_add_row_number)
        >>> df.pipe(pd_add_row_number, 'rn')
        >>> df.pipe(pd_add_row_number, col_group='type')
    '''
    if col_group is None:
        df = df.assign(**{col_name: lambda _: range(start, _.shape[0]+start)})
    else:
        df = df.assign(**{col_name: lambda _: _.groupby(col_group).cumcount()})

    if place_first:
        df = df.pipe(pd_select, f'{col_name}, *')

    return df

#endregion -----------------------------------------------------------------------------------------
#region Archive

#%%
def pd_select_simple(df: pd.DataFrame,
                     cols_before: str|list|np.ndarray|pd.Series = None,
                     cols_after: str|list|np.ndarray|pd.Series = None,
                     cols_drop: str|list|np.ndarray|pd.Series = None,
                     remaining = True) -> pd.DataFrame:
    '''DEPRECATED: Use `pd_select()`. Select columns to keep or drop from dataframe. Can be used to change order of columns.

    Args:
        df (pd.DataFrame): Dataframe.
        cols_before (str | list | np.ndarray | pd.Series, optional): Columns to keep at the start. Defaults to None.
        cols_after (str | list | np.ndarray | pd.Series, optional): Columns to keep at the end. Defaults to None.
        cols_drop (str | list | np.ndarray | pd.Series, optional): Columns to drop. Defaults to None.
        remaining (bool, optional): If true, the remaining columns (except the ones to drop) are placed between 'cols_before' and 'cols_after'. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with specified columns.

    Examples:
        >>> df.pipe(pd_select_simple, cols_before='type2', cols_after='value1', cols_drop='value5')
        >>> df.pipe(pd_select_simple, cols_before=['value2', 'value4'], remaining=False)
        >>> df.pipe(pd_select_simple, cols_before=pd_cols_archive(df, 'value2', 'value4'))
        >>> df.pipe(pd_select_simple, cols_before=['type1', *pd_cols_archive(df, 'value2', 'value4')])
        >>> df.assign(var=0).pipe(lambda _: pd_select_simple(_, cols_before=['var']))
        >>> df.assign(var1=0, var2=5, var3=10).pipe(lambda _: pd_select_simple(_, cols_before=pd_cols_archive(_, 'var1', 'var3')))
    '''
    if cols_before is None:
        cols_before = []
    else:
        cols_before = pd_to_series(cols_before).tolist()

    if cols_after is None:
        cols_after = []
    else:
        cols_after = pd_to_series(cols_after).tolist()

    if cols_drop is None:
        cols_drop = []
    else:
        cols_drop = pd_to_series(cols_drop).tolist()

    if remaining:
        cols_others = df.columns.difference(cols_before + cols_after, sort=False).tolist()
        cols_keep = cols_before + cols_others + cols_after
    else:
        cols_keep = cols_before + cols_after

    cols_keep = [x for x in cols_keep if x not in cols_drop]

    return df[cols_keep]

#%%
def pd_drop(df: pd.DataFrame,
            cols: str|list|np.ndarray|pd.Series = None,
            col_from: str = None,
            col_to: str = None) -> pd.DataFrame:
    '''DEPRECATED: Use `pd_select()`. Drop selected columns from dataframe.

    Args:
        df (pd.DataFrame): Dataframe.
        cols (str | list | np.ndarray | pd.Series, optional): Vector of columns to drop. Defaults to None (first column).
        col_from (str, optional): First column in series of columns to drop. Defaults to None (last column).
        col_to (str, optional): Last column in series of column to drop. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe after dropping specified columns.

    Notes:
        - Any value in 'cols' not in 'df' is ignored. 'col_from' and 'col_to' have to in in 'df'.

    Examples:
        >>> df.pipe(pd_drop, 'value2')
        >>> df.pipe(pd_drop, cols=['value2', 'type2'], col_from='value3', col_to='value5')
        >>> df.pipe(pd_drop, col_from='value3')
    '''
    if cols is not None:
        cols = pd_to_series(cols)
        cols_all = pd.Series(df.columns)
        cols = cols[cols.isin(cols_all)]
        df = df.drop(cols, axis=1)
    if (col_from is not None) | (col_to is not None):
        cols_all = pd.Series(df.columns)
        if col_from is not None:
            index_from = cols_all.tolist().index(col_from)
        else:
            index_from = 0
        if col_to is not None:
            index_to = cols_all.tolist().index(col_to) + 1
        else:
            index_to = len(cols_all)
        cols_to_drop = cols_all.iloc[index_from:index_to]

        df = df.drop(cols_to_drop, axis=1)
    return df

#%%
def pd_cols_archive(df: pd.DataFrame,
            col_from: str=None,
            col_to: str=None) -> list:
    '''Get column names between two column names for given dataframe.

    Args:
        df (pd.DataFrame): Dataframe.
        col_from (str, optional): First column in series of columns to return. Defaults to None.
        col_to (str, optional): Last column in series of column to return. Defaults to None.

    Returns:
        List: List of column names.

    Examples:
        >>> pd_cols_archive(df, None, 'value2')
        >>> ['type1', *pd_cols_archive(df, 'value2, 'value4')]
        >>> df.pipe(pd_select_simple, cols_before=pd_cols_archive(df, 'value2', 'value4'))
        >>> df.pipe(pd_drop, cols = pd_cols_archive(df, 'value2'))
    '''
    cols = pd.Series(df.columns)
    if col_from is not None:
        index_from = cols.tolist().index(col_from)
    else:
        index_from = 0
    if col_to is not None:
        index_to = cols.tolist().index(col_to) + 1
    else:
        index_to = len(cols)
    cols_to_select = cols.iloc[index_from:index_to].to_list()
    return cols_to_select

#endregion -----------------------------------------------------------------------------------------
