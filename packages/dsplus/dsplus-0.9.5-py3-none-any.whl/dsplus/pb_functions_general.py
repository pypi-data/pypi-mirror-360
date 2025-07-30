#region Libraries

#%%
import os
import shutil

import inspect

from typing import Literal, Callable, Any

import pandas as pd
import numpy as np

from scipy import interpolate

from statsmodels.nonparametric import smoothers_lowess
from scipy.signal import savgol_filter
from scipy.ndimage.filters import gaussian_filter1d

import pickle

from .pb_functions_pandas import *

pd.options.display.max_columns = None
pd.options.display.max_rows = 8

#endregion -----------------------------------------------------------------------------------------
#region Functions: Type Conversion

#%%
def as_numeric(value: int|float|str|list|np.ndarray|pd.Series) -> float|pd.Series:
    '''Convert provided value to number (float). Mainly useful for converting string to number. If numeric conversion is not possible, np.nan is returned and an error is not raised. Wrapper around pd.to_numeric(value, errors='coerce').

    Args:
        value (int | float | str | list | np.ndarray | pd.Series): Any object to convert to number. Typically string or vector of string.

    Returns:
        float | pd.Series: Number or vector of numbers with np.nan. Number/np.nan is returned if 'value' is int, float, or str. Otherwise seires is returned.

    Examples:
        >>> as_numeric('a')
        >>> as_numeric(['a', 2, '2', np.nan])
    '''
    # try:
    #     return float(value)
    # except (ValueError, TypeError):
    #     return np.nan

    value_numeric = pd.to_numeric(pd.Series(value), errors='coerce')

    if isinstance(value, int) | isinstance(value, float) | isinstance(value, str):
        value_numeric = value_numeric.iloc[0]

    return (value_numeric)

#endregion -----------------------------------------------------------------------------------------
#region Functions: File

#%%
def os_path(path: str|list|np.ndarray|pd.Series) -> str|pd.Series:
    '''Replace forward slash by back slash in path.

    Args:
        path (str | list | np.ndarray | pd.Series): Vector of pathnames.

    Returns:
        str|pd.Series: Pathname(s) with only back slashes. If 'path' is string literal, string literal is returned. Otherwise, Series is returned.

    Examples:
        >>> os_path(r'd:\try.txt')
        >>> os_path('d:\\try.txt')
        >>> os_path([r'd:\try.txt', 'd:\\try.txt'])
    '''
    v_path = pd_to_series(path)

    v_path = v_path.str.replace('\\', '/').str.replace('//', '/')

    if isinstance(path, str):
        return v_path.iloc[0]
    else:
        return v_path

#%%
def os_path_join(folders: str|list|np.ndarray|pd.Series,
                 files: str|list|np.ndarray|pd.Series,
                 extensions: str|list|np.ndarray|pd.Series= None) -> pd.Series:
    '''Vectorized function for joining folder and file paths.

    Args:
        folders (str | list | np.ndarray | pd.Series): Vector of folder paths.
        files (str | list | np.ndarray | pd.Series): Vector of file paths.
        extensions (str | list | np.ndarray | pd.Series): Vector of extension of all files. Do not include period. Defaults to None.

    Returns:
        Series: Series of full paths.

    Noted:
        - The length of the files, folders, and extensions can be: (a) all 1, (b) 1 for one and same for the other two, or (c) same for all three.

    Examples:
        >>> os_path_join(r'd:\folder', 'file')
        >>> os_path_join(r'd:\folder', 'file', 'txt')
        >>> os_path_join(r'd:\folder', ['file1', 'file2'], 'txt')
        >>> os_path_join([r'd:\folder1', r'd:/folder2'], 'file')
        >>> os_path_join([r'd:\folder1', r'd:/folder2'], ['file1', 'file2'], ['txt', 'csv'])
    '''
    v_folders = pd_to_series(folders)
    v_files = pd_to_series(files)
    v_extensions = pd_to_series(extensions)

    len_max = np.max([len(v_folders), len(v_files), len(v_extensions)])

    if len_max > 1:
        if len(v_folders) == 1:
            v_folders = v_folders.repeat(len_max)
        if len(v_files) == 1:
            v_files = v_files.repeat(len_max)
        if len(v_extensions) == 1:
            v_extensions = v_extensions.repeat(len_max)

    v_folders = v_folders.reset_index(drop = True)
    v_files = v_files.reset_index(drop = True)
    v_extensions = v_extensions.reset_index(drop = True)

    v_path = v_folders.str.cat(v_files, sep = os.path.sep)

    if extensions is not None:
        v_path = v_path.str.cat(v_extensions, sep = r'.')

    return (v_path)

#%%
def os_filename(v_pathnames: str|list|np.ndarray|pd.Series) -> pd.Series:
    '''Remove extension from pathnames.

    Args:
        v_pathnames (str | list | np.ndarray | pd.Series): Vector of pathnames.

    Returns:
        pd.Series: Series of filenames with extensions removed.

    Examples:
        >>> os_filename('try.txt')
        >>> os_filename(['try.txt.jpg', 'try2.txt'])
    '''
    v_pathnames = pd.Series([os.path.splitext(v_pathname)[0] for v_pathname in pd_to_series(v_pathnames)])

    return v_pathnames

#%%
def os_extension(v_pathnames: str|list|np.ndarray|pd.Series) -> pd.Series:
    '''Get extension from pathnames.

    Args:
        v_pathnames (str | list | np.ndarray | pd.Series): Vector of pathnames.

    Returns:
        pd.Series: Series of extensions.

    Examples:
        >>> os_extension(r'D:\try.txt')
        >>> os_extension([r'D:\try.txt.jpg', r'D:\try2.txt'])
    '''
    # v_pathnames = pd.Series([os.path.splitext(v_pathname)[1] for v_pathname in pd_to_series(v_pathnames)]).str.replace(r'.', '')
    v_pathnames = pd.Series([os.path.splitext(v_pathname)[1][1:] for v_pathname in pd_to_series(v_pathnames)])

    return v_pathnames

#%%
def os_basename(v_pathnames: str|list|np.ndarray|pd.Series, keep_extension = True) -> pd.Series:
    '''Get basenames from pathnames. Wrapper around 'os.path.basename()'.

    Args:
        v_pathnames (str | list | np.ndarray | pd.Series): Vector of pathnames.
        keep_extension (bool, True): If False, extensions are removed. Defaults to True.

    Returns:
        pd.Series: Series of basenames.

    Examples:
        >>> os_basename('D:\try.txt')
        >>> os_basename([r'D:\try.txt', r'D:\try2.txt'])
    '''
    v_pathnames = pd.Series([os.path.basename(v_pathname) for v_pathname in pd_to_series(v_pathnames)])

    if not keep_extension:
        # v_pathnames = pd.Series([os.path.splitext(v_pathname)[0] for v_pathname in pd_to_series(v_pathnames)])
        v_pathnames = os_filename(v_pathnames)

    return (v_pathnames)

#%%
def os_dirname(v_pathnames: str|list|np.ndarray|pd.Series) -> pd.Series:
    '''Get dirnames from pathnames. Wrapper around 'os.path.dirname()'.

    Args:
        v_pathnames (str | list | np.ndarray | pd.Series): Vector of pathnames.

    Returns:
        pd.Series: Series of dirnames.

    Examples:
        >>> os_dirname('D:\try.txt')
        >>> os_dirname(['D:\try.txt', 'D:\try2.txt'])
    '''
    v_pathnames = pd.Series([os.path.dirname(v_pathname) for v_pathname in pd_to_series(v_pathnames)])

    return (v_pathnames)

#%%
def os_list_dir(folder: str,
                full_names=True,
                extension: str=None,
                filter: Literal['files and folders', 'files', 'folders'] = 'files and folders') -> pd.Series:
    '''Get a list of files and folders in a given location.

    Args:
        folder (str): Folder location.
        full_names (bool, optional): If true, full paths of names are returned. If false, only basenames are returned. Defaults to True.
        extension (str, optional): Extension to filter. Only specify extension without the preceeding period character. Defaults to None.
        filter (int, optional): Filter files or folders only. Acceptable values are 'files and folders', 'files', and 'folders'. Defaults to 'files and folders'.

    Returns:
        pd.Series: Series of file and directory names.
    '''
    # [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.tif')]
    files = os.listdir(folder)

    if filter == 'files':
        files = [file for file in files if os.path.isfile(os.path.join(folder, file))]
    elif filter == 'folders':
        files = [file for file in files if not os.path.isfile(os.path.join(folder, file))]

    files = pd.Series(files)

    if full_names:
        files = folder + '/' + files

    if extension is not None:
        files = files[files.str.endswith(fr'.{extension}')]

    return (files)

#%%
def os_list_dir_recursive(folder: str) -> pd.DataFrame:
    '''List all files and folders in given location recursively.

    Args:
        folder (str): Folder location.

    Returns:
        pd.DataFrame: A dataframe with 4 columns, 'type': file or folder, 'name_full': full path and name, 'name_base': basename, and 'name_ext': extension (blank if non-existent).
    '''
    # files = pd.Series([os.path.join(root, f_name) for \
    #     root, d_names, f_names in os.walk(folder)\
    #     for f_name in f_names])
    # folders = pd.Series([os.path.join(root, d_name) for \
    #     root, d_names, f_names in os.walk(folder)\
    #     for d_name in d_names])
    # df_files = pd.DataFrame({'name_full': files}).assign(type = 'file')
    # df_folders = pd.DataFrame({'name_full': folders}).assign(type = 'folder')
    # df_dir = \
    #     (df_files
    #         .pipe(pd_concat_rows, df_folders)
    #         .assign(name_dir = lambda _: [os.path.dirname(y) for y in _['name_full']])
    #         .assign(name_base = lambda _: [os.path.basename(y) for y in _['name_full']])
    #         .pipe(pd_select, 'type, *')
    #     )
    
    v = []
    for root, d_names, f_names in os.walk(folder):
        for d_name in d_names:
            v.append(['folder', os.path.join(root, d_name), root, d_name, ''])
        for f_name in f_names:
            v.append(['file', os.path.join(root, f_name), root, f_name, os.path.splitext(f_name)[1][1:]])
    
    df_dir = pd.DataFrame(v, columns=['type', 'name_full', 'name_dir', 'name_base', 'name_ext'])

    return (df_dir)

#%%
def os_read_lines(name_file: str, remove_newline = True) -> pd.Series:
    '''Read lines from text file.

    Args:
        name_file (str): Filename.
        remove_newline (bool, optional): If true, the newline character ('\n') is removed from each line. Defaults to True.

    Returns:
        pd.Series: Series with each line stored as a string element.
    '''
    with open(name_file, 'r', errors='replace') as file:
        content_file = file.readlines()
    content_file=pd.Series(content_file)

    if remove_newline:
        content_file = content_file.str.replace('\n', '')

    return content_file

#%%
def os_write_lines(content_file: pd.Series, name_file: str, backup=True) -> None:
    '''Write lines to text file.

    Args:
        content_file (pd.Series of str): Series with each line stored as a string element.
        name_file (str): Filename.
        backup (bool, optional): If true, a backup of the original file is added. The backup file will have incremental two digit index as suffix (_backup00, _backup01, etc.). Defaults to True.

    Notes:
        - First string in 'content_file' is checked. If it doesn't end in newline character ('\n'), it is added to all strings in 'content_file'.
    '''
    if backup & os.path.isfile(name_file):
        backup_file(name_file)

    if not content_file.iloc[0:1].str.endswith('\n').any():
        content_file = content_file + '\n'

    with open(name_file, 'w') as file:
        file.writelines(content_file)

#%%
def pickle_read(name_file: str, add_extension=True) -> Any:
    '''Read pickle file.

    Args:
        name_file (str): Filename.
        add_extension (bool, optional): If True, '.pickle' extension is added to the filename. Defaults to True.

    Returns:
        any: Object stored in pickle file.

    Examples:
        >>> var = pickle_read('file')
        >>> var = pickle_read('file.pickle')
    '''
    if add_extension:
        name_file += '.pickle'
    with open(name_file, 'rb') as f:
        return (pickle.load(f))

#%%
def pickle_write(object_to_wite,
                 name_file: str=None,
                 add_extension=True,
                 backup = True) -> None:
    '''Write pickle file.

    Args:
        object_to_wite (any): Object to write.
        name_file (str, optional): Filename. If set to None, the name of the variable provided to 'object_to_write' is used (of "unnamed" if name of varaible could not be read). Defaults to None.
        add_extension (bool, optional): If True, '.pickle' extension is added to the filename. Defaults to True.
        backup (bool, optional): If true, a backup of the original file is added. The backup file will have incremental two digit index as suffix (_backup00, _backup01, etc.). Defaults to True.
    
    Examples:
        >>> pickle_write(var, 'file')
        >>> pickle_write(var, 'file.pickle')
        >>> pickle_write(var)
        >>> df.pipe(pickle_write)
    '''
    if name_file is None:
        _frame = inspect.currentframe().f_back
        _variables = {id(v): k for k, v in _frame.f_locals.items()}
        _var_name = _variables.get(id(name_file), 'unnamed')
        name_file = _var_name
    if add_extension:
        name_file += '.pickle'
    if backup:
        if os.path.isfile(name_file):
            backup_file(name_file)
    with open(name_file, 'wb') as f:
        pickle.dump(object_to_wite, f)

#%%
def get_copy_filename(filename_original: str, suffix='.backup', extension='bkp') -> str:
    '''Get a filename with suffix.

    Args:
        filename_original (str): Original filename.
        suffix (str, optional): Suffix to add. Defaults to '.backup'.
        extension (str, optional): File extension. Defaults to '.bkp'.

    Returns:
        str: Updated filename.
    '''
    temp_folder = os.path.dirname(filename_original)
    if temp_folder == '':
        temp_folder = os.getcwd()
        filename_original = os.path.join(temp_folder, filename_original)

    filename_original_backup = fr"{filename_original}{suffix}"
    temp_files = [os.path.join(temp_folder, f) for f in os.listdir(temp_folder)]
    temp_files = [f for f in temp_files if filename_original_backup in f]
    if len(temp_files) == 0:
        max_id = 0
    else:
        temp_id = pd.Series(temp_files).str.replace(filename_original_backup, '').str.replace(rf'.{extension}', '').astype('int')
        max_id = max(temp_id)
    current_id = max_id + 1
    filename_original_backup = f"{filename_original}{suffix}{str(current_id).zfill(2)}"
    if extension is not None and extension != '':
        filename_original_backup = f'{filename_original_backup}.{extension}'

    return filename_original_backup

#%%
def backup_file(name_file: str) -> None:
    '''Create a backup file. The backup file will have incremental two digit index as suffix (.backup00.bkp, .backup01.bkp, etc.).

    Args:
        name_file (str): Filename to backup.
    '''
    name_file_backup = get_copy_filename(name_file)
    shutil.copy(name_file, name_file_backup)

#endregion -----------------------------------------------------------------------------------------
#region Functions: String

#%%
#TODO The behavior of array concatenation with empty entries is deprecated. In a future version, this will no longer exclude empty items when determining the result dtype. To retain the old behavior, exclude the empty entries before the concat operation. 
def str_concat(*v_str: str|list|np.ndarray|pd.Series) -> pd.Series:
    '''Vectorized function for joining strings.

    Args:
        *v_str (str | list | np.ndarray | pd.Series): Vector of strings.

    Returns:
        pd.Series: Series of concatenated strings.

    Notes:
        - Each vector can be either of length 1 or of a constant length.

    Examples:
        >>> str_concat('x', '_', ['y', 'z'])
    '''
    v_str = [pd.Series(val_str).to_numpy() for val_str in v_str]
    v_str_len = [len(x) if not isinstance(x, str) else 1 for x in v_str]

    if len(v_str_len) == 0:
        str_c = ''
        for str_current in v_str:
            str_c += str_current
        return (str_c)
    else:
        max_str_len = max(v_str_len)

        str_c = pd.Series(['']).repeat(max_str_len).reset_index(drop = True)

        for str_current, str_len in zip(v_str, v_str_len):
            temp_str_current = pd_to_series(str_current)
            temp_str_current = temp_str_current.replace(np.nan, '')
            if str_len < max_str_len:
                temp_str_current = temp_str_current.repeat(max_str_len)
            temp_str_current = temp_str_current.reset_index(drop = True)

            str_c = str_c.str.cat(temp_str_current.astype(str))

        return (str_c.to_numpy())

#%%
def str_join(v_str: list|np.ndarray|pd.Series, join_sep: str = ',') -> str:
    '''Join multiple strings into a single string with a join separator. Wrapper around 'join()'.

    Args:
        v_str (list | np.ndarray | pd.Series): Vector of strings.
        join_sep (str, optional): Join separator. Defaults to ','.

    Returns:
        str: Joined string.

    Examples:
        >>> str_join(['a', 'b', 5], '; ')
    '''
    return join_sep.join(map(str, v_str))

#endregion -----------------------------------------------------------------------------------------
#region Functions: Others

#%%
def smoothen_line(y:list|np.ndarray|pd.Series, x:list|np.ndarray|pd.Series = None, method:Literal['svg', 'lowess', 'ewm', 'gaussian'] = 'gaussian', window_frac:float = 0.05, window_count:int = None, span:float = 3, polyorder:int = 2, sigma:float = 1) -> pd.Series:
    '''Smoothen line using various methods.

    Args:
        y (list | np.ndarray | pd.Series): Vector of y values.
        x (list | np.ndarray | pd.Series, optional): Vector of x values. Defaults to None. Only applicable if 'method' is 'lowess'.
        method (str, optional): 'svg' for Savitzky-Golay Filter ('scipy.signal.savgol_filter()'), 'lowess' for Lowess Smoothing ('statsmodels.nonparametric.smoothers_lowess()'), 'ewm' for Exponential Moving Average ('pd.ewm()'), 'gaussian' for Gaussian Filter ('scipy.ndimage.filters.gaussian_filter1d'). Defaults to 'gaussian'.
        window_frac (float, optional): Fraction of data points for local weighting. Defaults to 0.05. Only applicable if 'method' is 'svg' or 'lowess'.
        window_count (int, optional): Number of data points (window size) for local weighting. Defaults to None. Only applicable if 'method' is 'svg' or 'lowess'.
        span (float, optional): Decay. Defaults to 3. Only applicable if 'method' is 'ewm'.
        polyorder (int, optional): Order of polynomial to fit. Defaults to 2. Only applicable if 'method' is 'svg'.
        sigma (float, optional): Standard deviation for Gaussian kernel. Only applicable if 'method' is 'guassian'.

    Returns:
        Series: Series of smoothed y values.

    Notes:
        - 'svg' requires 'polyorder' and one of 'window_frac' and 'window_count'.
        - 'lowess' requires one of 'window_frac' and 'window_count'.
        - 'ewm' requires 'span'.
        - 'gaussian' requires 'sigma'.
        - 'svg', 'ewm', and 'gaussian' require 'y' values at evenly spaced 'x' values.

    Examples:
        >>> smoothen_line(df['y'])
        >>> smoothen_line(df['y'], method = 'svg', window_frac = 0.03)
        >>> smoothen_line(df['y'], df['x'], method = 'lowess')
        >>> smoothen_line(df['y'], df['x'], method = 'lowess, window_frac = 0.03, polyorder = 3)
        >>> smoothen_line(df['y'], method = 'ewm')
        >>> smoothen_line(df['y'], method = 'ewm', span = 3)
        >>> smoothen_line(df['y'], method = 'gaussian', sigma = 1.5)
    '''
    y = pd_to_series(y)
    if method == 'svg':
        if window_count is None:
            window_count = int(np.round(window_frac*len(y)))
        y_smooth = savgol_filter(y, window_count, polyorder)
    elif method == 'lowess':
        if window_frac is None:
            window_frac = window_count/len(y)
        x = pd_to_series(x)
        y_smooth = smoothers_lowess.lowess(y, x, frac = window_frac)[:, 1]
    elif method == 'ewm':
        y_smooth = y.ewm(span=span, adjust=False).mean()
    elif method == 'gaussian':
        y_smooth = gaussian_filter1d(y, sigma=sigma)
    else:
        return (pd.Series())

    y_smooth = pd.Series(y_smooth)
    return (y_smooth)

#%%
def interp_1d(x: list|np.ndarray|pd.Series, y: list|np.ndarray|pd.Series, x_out: float|list|np.ndarray|pd.Series = None, fill_value: str = 'extrapolate') -> pd.Series:
    '''Estimate values through linear interpolation. Can be used to fill NA values. Can fill or extrapolate values outside bounds.

    Args:
        x (list | np.ndarray | pd.Series): Vector of x values.
        y (list | np.ndarray | pd.Series): Vector of y values.
        x_out (float | list | array | Series, optional): Vector of x values for which y values are to be estimated. Defaults to None.
        fill_value (str, optional): Fill value for 'x_out' values outside the bounds of 'x'. Acceptable values are 'extrapolate' to extrapolate values, 'na' to set as NA values, 'ffill' to do a forward fill, 'bfill' to do a back fill, and 'fill' to do a forward and backward fill. Defaults to 'extrapolate'.

    Returns:
        pd.Series: Series of y values corresponding to x_out.

    Notes:
        - If 'x_out' is None, 'x' is taken as 'x_out'. This is especially useful for filling NA values in 'y'.

    Examples:
        >>> df = pd.DataFrame(dict(x = [1,2,3,5,10,4],
                                   y = [10,20,np.nan,50,np.nan,np.nan]))
        >>> interp_1d(df['x'], df['y'])
        >>> interp_1d(df['x'], df['y'], 2.5)
        >>> interp_1d(df['x'], df['y'], [0, 2.5, 11])
        >>> df.assign(x_inter = lambda _: interp_1d(_['x'], _['y']))
        >>> df.assign(x_inter = lambda _: interp_1d(_['x'], _['y'], fill_value='na'))
        >>> df.assign(x_inter = lambda _: interp_1d(_['x'], _['y'], fill_value='fill'))
    '''
    df = pd.DataFrame({'x': x,
                       'y': y})
    if fill_value == 'extrapolate':
        f_interp = interpolate.interp1d(df.dropna()['x'], df.dropna()['y'], fill_value='extrapolate', bounds_error=False)
    else:
        f_interp = interpolate.interp1d(df.dropna()['x'], df.dropna()['y'], fill_value=np.nan, bounds_error=False)

    if x_out is None:
        y_out = f_interp(x)
        y_out = pd.Series(y_out)
        y_out = np.where(y_out.isna(), y, y_out)
        y_out = pd.Series(y_out)
    else:
        y_out = f_interp(x_out)
        y_out = pd.Series(y_out)

    if fill_value == 'ffill' or fill_value == 'fill':
        y_out = y_out.fillna(method='ffill')
    if fill_value == 'bfill' or fill_value == 'fill':
        y_out = y_out.fillna(method='bfill')

    return (y_out)

#%%
def error_to_na(command, na_result = np.nan) -> Any:
    '''Takes a command and returns None when the command raises an error.

    Args:
        command (lambda function): An ananymous lambda function with no arguments.
        na_result (any): Result if command raises an error. Defaults to np.nan.

    Returns:
        any: Either the result of the function or None if the function raises an error.

    Examples:
        >>> error_to_na(lambda: float('12'))
        >>> error_to_na(lambda: float('A12'))
    '''
    try:
        result = command()
        return (result)
    except Exception as e:
        return (na_result)

#%%
def np_seq(primary: int|float = None, end: int|float = None, by: int|float = None, count: int|float = None) -> np.ndarray:
    '''Return evenly spaced values within a given sepcification. Wrapper around 'np.arange()' and 'np.linspace()'.

    Args:
        primary (int | float, optional): If this is the only input, then this is the end of the sequeence. If there are multiple inputs, then this is the start of the sequence. Defaults to None.
        end (int | float, optional): End of the sequence. Defaults to None.
        by (int | float, optional): Spacing, difference between successive numbers in the sequence. Defaults to None.
        count (int | float, optional): Number of terms in the sequence. Defaults to None.

    Returns:
        np.ndarray: Vector of sequence.

    Notes:
        - If only 'primary' is provided, a sequence from 1 to 'primary' (excl) with a difference of 1 is generated.
        - If 'primary' and 'end' are provided, a sequence from 'primary' to 'end' (excl) with a difference of 1 is generated.
        - If 'primary', 'end', and 'by' are provided, a sequence from 'primary' to 'end' (excl) with a difference of 'by' is generated.
        - If 'primary', 'end', and 'count' are provided, a sequence from 'primary' to 'end' (incl) with a 'count' numbers is generated.
        - If 'primary', 'by', and 'count' are provided, a sequence from 'primary' with a difference of 'by' and with 'count' numbers is generated.
        - If 'end', 'by', and 'count' are provided, a sequence upto 'end' (incl) with a difference of 'by' and with 'count' numbers is generated.
        - Inclusive vs exclusive rules:
            - 'primary' is always inclusive if provided
            - 'end' is inclusive if and only if 'count' is provided

    Examples
        >>> np_seq(10)
        >>> np_seq(1, 10)
        >>> np_seq(1, 10, 2)
        >>> np_seq(1, 10, 3)
        >>> np_seq(1, 10, count=4)
        >>> np_seq(1, by=2, count=6)
        >>> np_seq(end=10, by=2, count=6)
    '''
    if pd.Series([primary, end, by]).notna().all():
        seq = np.arange(primary, end, by)
    elif pd.Series([primary, end, count]).notna().all():
        seq = np.linspace(primary, end, count)
    elif pd.Series([primary, by, count]).notna().all():
        seq = np.arange(primary, primary + by*count, by)
    elif pd.Series([end, by, count]).notna().all():
        seq = np.arange(end - by*(count-1), end + by, by)
    elif pd.Series([primary, end]).notna().all():
        seq = np.arange(primary, end, 1)
    elif pd.Series([end, by, count]).isna().all():
        seq = np.arange(primary)

    return seq

#%%
def combine_arguments(func: Callable, args: tuple, kwargs: dict) -> dict:
    '''Consolidate all functions arguments (arguments, keyword arguments, and default arguments) into a single dictionary. Mainly useful in decorators.

    Args:
        func (Callable): Function.
        args (tuple): Function arguments from *args.
        kwargs (dict): Function keyword arguments from **kwargs.

    Returns:
        dict: Single dictionary with all arguments, keyword arguments, and default arguments.
    '''
    sig_func = inspect.signature(func)
    args_default = [
            k for k, v in sig_func.parameters.items() if v.default == inspect.Signature.empty
    ]
    kwargs_default = {
            k: v.default for k, v in sig_func.parameters.items() if v.default != inspect.Signature.empty
    }

    # print (f'args: \n{args},\nkwargs: \n{kwargs},\nargs_defaults: \n{args_default}, \nkwargs_default: \n{kwargs_default}')

    args = {k:v for k, v in zip(args_default, args)}

    return (args | kwargs_default | kwargs)

#endregion -----------------------------------------------------------------------------------------
