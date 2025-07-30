#region Library

#%%
import pandas as pd
import numpy as np
import dsplus as ds

#%%
import importlib
importlib.reload(ds)

#endregion -----------------------------------------------------------------------------------------
#region Set Operations

#%%
def test_set_union_1():
    v1 = [0,1,2]
    v2 = [1,2,3]

    v = ds.set_union(v1, v2).tolist()

    assert v == [0,1,2,3]

def test_set_union_2():
    v1 = [0,1,2]
    v2 = [3,4]

    v = ds.set_union(v1, v2).tolist()

    assert v == [0,1,2,3,4]

def test_set_intersection_1():
    v1 = [0,1,2]
    v2 = [1,2,3]

    v = ds.set_intersection(v1, v2).tolist()

    assert v == [1,2]

def test_set_intersection_2():
    v1 = [0,1,2]
    v2 = [3,4]

    v = ds.set_intersection(v1, v2).tolist()

    assert v == []

def test_set_diff_1():
    v1 = [0,1,2]
    v2 = [1,2,3]

    v = ds.set_diff(v1, v2).tolist()

    assert v == [0]

def test_set_diff_2():
    v1 = [0,1,2]
    v2 = [3,4]

    v = ds.set_diff(v1, v2).tolist()

    assert v == [0,1,2]

#endregion -----------------------------------------------------------------------------------------
#region Type Conversion

#%%
def test_pd_to_series_1():
    assert ds.pd_to_series([1,2,3]).equals(pd.Series([1,2,3]))

#%%
def test_pd_to_series_2():
    assert ds.pd_to_series([]).equals(pd.Series([]))

#%%
def test_pd_to_series_3():
    assert ds.pd_to_series(np.array([1,2,3])).equals(pd.Series(np.array([1,2,3])))

#%%
def test_pd_to_series_4():
    assert ds.pd_to_series(pd.Series([1,2,3])).equals(pd.Series([1,2,3]))

#%%
def test_pd_to_series_5():
    assert ds.pd_to_series(pd.Series([1,2,3]).index).equals(pd.Series([0,1,2]))

#%%
def test_pd_to_numpy_1():
    assert np.array_equal(ds.pd_to_numpy([1,2,3]), np.array([1,2,3]))

#%%
def test_pd_to_numpy_2():
    assert np.array_equal(ds.pd_to_numpy([]), np.array([]))

#%%
def test_pd_to_numpy_3():
    assert np.array_equal(ds.pd_to_numpy(np.array([1,2,3])), np.array([1,2,3]))

#%%
def test_pd_to_numpy_4():
    assert np.array_equal(ds.pd_to_numpy(pd.Series([1,2,3])), np.array([1,2,3]))

#%%
def test_pd_to_numpy_5():
    assert np.array_equal(ds.pd_to_numpy(pd.Series([1,2,3]).index), np.array([0,1,2]))

#endregion -----------------------------------------------------------------------------------------
#region Slice

#%%
def test_pd_select_1():
    df = pd.DataFrame(columns = ['v'+str(_) for _ in range(21)])

    df_select = df.pipe(ds.pd_select, 'str.startswith("v2"), *, -str.startswith("v1"), -v8')

    assert df_select.columns.tolist() == ['v2', 'v20', 'v0', 'v3', 'v4', 'v5', 'v6', 'v7', 'v9']

#%%
def test_pd_select_2():
    df = pd.DataFrame(columns = ['v'+str(_) for _ in range(21)])

    df_select = df.pipe(ds.pd_select, '-:v5, -v8:')

    assert df_select.columns.tolist() == ['v6', 'v7']

#%%
def test_pd_select_3():
    df = pd.DataFrame(columns = ['v'+str(_) for _ in range(21)]).astype(dict(v5=int, v15=int, v0='category'))

    df_select = df.pipe(ds.pd_select, 'select_dtypes("number"), *, -v8:v13, -select_dtypes("category")')

    assert df_select.columns.tolist() == ['v5', 'v15', 'v1', 'v2', 'v3', 'v4', 'v6', 'v7', 'v14', 'v16', 'v17', 'v18', 'v19', 'v20']

#endregion -----------------------------------------------------------------------------------------
#region Concat

#%%
def test_pd_concat_series_1():
    assert ds.pd_concat_series(pd.Series([1,2,3]), 4).tolist() == [1,2,3,4]

#%%
def test_pd_concat_series_2():
    assert ds.pd_concat_series(pd.Series([1,2,3]), [4,5]).tolist() == [1,2,3,4,5]

#%%
def test_pd_concat_rows_1():
    df1 = ds.pd_df(x = [1,2,3],
                   y = [4,5,6])
    df2 = ds.pd_df(x = [10,20],
                   y = [40,50])
    df = ds.pd_concat_rows(df1, df2)
    df_test = ds.pd_df(x = [1,2,3,10,20],
                       y = [4,5,6,40,50])

    assert df.equals(df_test)

#%%
def test_pd_concat_rows_2():
    df1 = ds.pd_df(x = [1,2,3],
                   y = [4,5,6])
    df2 = ds.pd_df()
    df = ds.pd_concat_rows(df1, df2)

    assert df.equals(df1)

#%%
def test_pd_concat_cols_1():
    df1 = ds.pd_df(x = [1,2,3],
                   y = [4,5,6])
    df2 = ds.pd_df(a = [10,20,30],
                   b = [40,50,60])
    df = ds.pd_concat_cols(df1, df2)
    df_test = ds.pd_df(x = [1,2,3],
                       y = [4,5,6],
                       a = [10,20,30],
                       b = [40,50,60])

    assert df.equals(df_test)

#%%
def test_pd_concat_cols_2():
    df1 = ds.pd_df(x = [1,2,3],
                   y = [4,5,6])
    df2 = ds.pd_df()
    df = ds.pd_concat_cols(df1, df2)

    assert df.equals(df1)

#endregion -----------------------------------------------------------------------------------------
#region Merge

#%%
def test_pd_merge_asof_1():
    df1 = pd.DataFrame({'index': [1,10,20,30],
                        'name1': ['a', 'b', 'c', 'd']})
    df2 = pd.DataFrame({'index': [5, 12, 26, 35],
                        'name2': ['aa', 'bb', 'cc', 'dd']})

    df = ds.pd_merge_asof(df1, df2, on='index')
    df_test = df1.assign(name2 = ['aa', 'bb', 'cc', 'dd'])

    assert df.equals(df_test)

#%%
def test_pd_merge_asof_2():
    df1 = pd.DataFrame({'index': [1,10,20,30],
                        'name1': ['a', 'b', 'c', 'd']})
    df3 = pd.DataFrame({'index': [5, 26],
                        'name3': ['aaa', 'ccc']})

    df = ds.pd_merge_asof(df1, df3, on='index')
    df_test = df1.assign(name3 = ['aaa', 'ccc', 'ccc', np.nan])

    assert df.equals(df_test)

#%%
def test_pd_merge_asof_3():
    df1 = pd.DataFrame({'index': [1,10,20,30],
                        'name1': ['a', 'b', 'c', 'd']})
    df3 = pd.DataFrame({'index': [5, 26],
                        'name3': ['aaa', 'ccc']})

    df = ds.pd_merge_asof(df1, df3, on='index', one_to_many=True)
    df_test = df1.assign(name3 = ['aaa', np.nan, 'ccc', np.nan])

    assert df.equals(df_test)

#%%
def test_pd_merge_asof_4():
    df1 = pd.DataFrame({'index_start': [10,20,30,40]})
    df2 = pd.DataFrame({'index_end': [2,5,12,24,25,32,46,50]})

    df = ds.pd_merge_asof(df1, df2, left_on='index_start', right_on='index_end')
    df_test = pd.DataFrame({'index_start': [10, 20, 30, 40],
                            'index_end': [12, 24, 32, 46]})

    assert df.equals(df_test)

#%%
def test_pd_merge_asof_5():
    df1 = pd.DataFrame({'index_start': [10,20,30,40]})
    df2 = pd.DataFrame({'index_end': [2,5,12,24,25,32,46,50]})

    df = ds.pd_merge_asof(df1, df2, left_on='index_start', right_on='index_end', one_to_many=True)
    df_test = pd.DataFrame({'index_start': [10, 20, 20, 30, 40, 40],
                            'index_end': [12, 24, 25, 32, 46, 50]})

    assert df.equals(df_test)

#%%
def test_pd_merge_between_indices_1():
    df_index_between = pd.DataFrame({'index_start': [10,20,30,40],
                                     'index_end': [12,24,39,50]})
    df_index_value = pd.DataFrame({'index': [5,10,11,12,15,22,30,35,50,51],
                                   'index2': [5,10,11,12,15,22,30,35,50,51]})

    df = ds.pd_merge_between_indices(df_index_between, df_index_value,
                                  left_min_col='index_start', left_max_col='index_end',
                                  right_col='index')
    df_test = pd.DataFrame({'index_start': [10, 10, 10, 20, 30, 30, 40],
                            'index_end': [12, 12, 12, 24, 39, 39, 50],
                            'index2': [10, 11, 12, 22, 30, 35, 50]})

    assert df.equals(df_test)

#%%
def test_pd_merge_between_indices_2():
    df_index_between = pd.DataFrame({'index_start': [10,20,30,40],
                                     'index_end': [12,24,39,50]})
    df_index_value = pd.DataFrame({'index': [5,10,11,12,15,22,50,51],
                                   'index2': [5,10,11,12,15,22,50,51]})

    df = ds.pd_merge_between_indices(df_index_between, df_index_value,
                                  left_min_col='index_start', left_max_col='index_end',
                                  right_col='index')
    df_test = pd.DataFrame({'index_start': [10, 10, 10, 20, 30, 40],
                            'index_end': [12, 12, 12, 24, 39, 50],
                            'index2': [10, 11, 12, 22, np.nan, 50]})

    assert df.equals(df_test)

#endregion -----------------------------------------------------------------------------------------
#region Conditionals

#%%
def test_pd_if_else_1():
    assert ds.pd_if_else(5 > 6, 5, 6) == 6

#%%
def test_pd_if_else_2():
    df = ds.pd_df(x = [1,2,3],
                  y = [-1,2,4],
                  a = ['a', 'a', 'a'],
                  b = ['b', 'b', 'b'])
    assert ds.pd_if_else(df['x'] > df['y'], df['a'], df['b']).tolist() == ['a','b','b']

#%%
def test_pd_case_when_1():
    df = ds.pd_df(x = np.arange(5),
                  y = np.arange(8,3,-1))

    v = ds.np_case_when(df['x']==df['y'], 'a',
                        df['x']%2==0, 'b',
                        True, df['y'])

    assert v.tolist() == ['b', '7', 'b', '5', 'a']

#endregion -----------------------------------------------------------------------------------------
#region Index

#%%
def test_pd_reset_column_1():
    df_multi_column = pd.DataFrame({('value1', 't1'): {'c1': 1, 'c2': 2, 'c3': 3},
                                    ('value1', 't2'): {'c1': 0, 'c2': 5, 'c3': 1},
                                    ('value2', 't1'): {'c1': 6, 'c2': 7, 'c3': 8},
                                    ('value2', 't2'): {'c1': 5, 'c2': 10, 'c3': 6}})

    df = df_multi_column.pipe(ds.pd_reset_column)
    df_test = pd.DataFrame({'value1_t1': [1, 2, 3],
                            'value1_t2': [0, 5, 1],
                            'value2_t1': [6, 7, 8],
                            'value2_t2': [5, 10, 6]},
                            index = ['c1', 'c2', 'c3'])

    assert df.equals(df_test)

def test_pd_reset_column_2():
    df_multi_column = pd.DataFrame({('value1', 't1'): {'c1': 1, 'c2': 2, 'c3': 3},
                                    ('value1', 't2'): {'c1': 0, 'c2': 5, 'c3': 1},
                                    ('value2', 't1'): {'c1': 6, 'c2': 7, 'c3': 8},
                                    ('value2', 't2'): {'c1': 5, 'c2': 10, 'c3': 6}})

    df = df_multi_column.pipe(ds.pd_reset_column, rev=True, join_sep='__', join_sep_name='_')
    df_test = pd.DataFrame({'t1__value1': [1, 2, 3],
                            't2__value1': [0, 5, 1],
                            't1__value2': [6, 7, 8],
                            't2__value2': [5, 10, 6]},
                            index = ['c1', 'c2', 'c3'])

    assert df.equals(df_test)

#%%
def test_pd_set_colnames_1():
    df = pd.DataFrame(columns = ['c1', 'c2', 'c3'])

    df = ds.pd_set_colnames(df, ['v1', 'v2', 'v3'])

    assert df.columns.tolist() == ['v1', 'v2', 'v3']

def test_pd_set_colnames_2():
    df = pd.DataFrame(columns = ['c1', 'c2', 'c3'])

    df = ds.pd_set_colnames(df, ['v1', 'v2', 'v3', 'v4'])

    assert df.columns.tolist() == ['v1', 'v2', 'v3']

def test_pd_set_colnames_3():
    df = pd.DataFrame(columns = ['c1', 'c2', 'c3'])

    df = ds.pd_set_colnames(df, col_names=['v1', 'v2'])

    assert df.columns.tolist() == ['v1', 'v2', '_2']

def test_pd_clean_colnames_1():
    df = pd.DataFrame(columns = ['x a(&a-b_ m  '])

    df = ds.pd_clean_colnames(df)

    assert df.columns.tolist() == ['x_a_a_b_m_']

def test_pd_clean_colnames_2():
    df = pd.DataFrame(columns = ['x a(&a-b_ m  '])

    df = ds.pd_clean_colnames(df, trailing_underscore=False)

    assert df.columns.tolist() == ['x_a_a_b_m']

def test_pd_clean_colnames_3():
    df = pd.DataFrame(columns = ['x a(&a-b_ m  '])

    df = ds.pd_clean_colnames(df, trailing_underscore=False, replace_symbols=False)

    assert df.columns.tolist() == ['x_aa_b_m']

#endregion -----------------------------------------------------------------------------------------
#region Others

#%%
def test_pd_definition_1():
    df_ds = ds.pd_dataframe(x = [1,2,3],
                            y = 4)
    df_pd = pd.DataFrame(dict(x = [1,2,3],
                              y = 4))

    assert df_pd.equals(df_ds)

#%%
def test_pd_definition_2():
    df_ds = ds.pd_df()
    df_pd = pd.DataFrame()

    assert df_pd.equals(df_ds)

def test_pd_split_column_1():
    df = ds.pd_dataframe(sn = [1,2,3],
                         c = ['a_b', 'mm_nnn', 'x_y'])

    df_split = ds.pd_split_column(df, '_', column_original='c', columns_new=['c1', 'c2'])

    df_split_check = pd.concat([df,
                                df['c'].str.split('_', expand=True).set_axis(['c1', 'c2'], axis=1)],
                                axis=1)

    assert df_split.equals(df_split_check)

def test_pd_split_column_2():
    df = ds.pd_dataframe(sn = [1,2,3],
                         c = ['a_b', 'mm_nnn', 'x_y_z'])

    df_split = ds.pd_split_column(df, '_', column_original='c')

    df_split_check = pd.concat([df,
                                df['c'].str.split('_', expand=True)],
                                axis=1)

    assert df_split.equals(df_split_check)

#endregion -----------------------------------------------------------------------------------------
