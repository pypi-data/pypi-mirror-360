#region Libraries

#%%
from typing import Literal, Self, Callable, Any

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio

from .pb_functions_general import *

#endregion -----------------------------------------------------------------------------------------
#region Functions

#%%
def px_add_trace_data(fig_original, *figs):
    '''Add trace(s) to plotly figure.

    Args:
        fig_original (Plotly figure): Plotly figure to add trace to.
        *figs (Plotly traces): Plotly traces to add to the figure.

    Returns:
        Plotly figure: Plotly figure with traces added.
    '''
    # TODO not working (only takes first fig) - Update: Should work now
    for fig in figs:
        if fig_original is not None:
            for i in range(len(fig.data)):
                fig_original.add_trace(fig.data[i])
        else:
            fig_original = fig
    return fig_original

#endregion -----------------------------------------------------------------------------------------
#region Class

#TODO Documentation for add_*.
#TODO What does "aes_" methods do?

#%%
class px_Plot():
    '''An interface for declaratively creating plotly plots.

    Following are the main methods:

        - facet(): Add faceting.
        - marginal(): Add marginal plots.
        - transform(): Add log-scale to axes.
        - add_*(): Add different traces. Not all traces have been implemented.
        - add(): Add traces directly from plotly trace objects.
        - label(): Add x and y labels and plot title.
        - legend(): Update legend properties.
        - colorbar(): Update colorbar legend properties.
        - size(): Update plot size.
        - axis(), axis_x(), axis_y(): Update axis properties.
        - layout(): Update layout properties.
        - show(): Show plot.
        - write_image(): Write plot to static image file.
        - write_html(): Write plot to dynamic html file.
        - get_fig(): Get plotly figure object.

    Notes:
        - Every method (except 'get_fig()') returns the original object, which facilitates chaining.
        - Most common traces have been implemented using the 'add_*()' methods. Use 'add_trendline()' to add trendlines. Traces not implemented yet can be added using the 'add()' method.
        - 'facet()', 'marginal()', and 'transform' have to come before 'add_*()'. Every other method has to come after 'add_*()'.
        - Use 'show()' to show the figure. Further chaining is allowed.
        - Use 'write_image()' and/or 'write_html()' to save the figure. Further chaining is allowed.
        - The original plotly figure object can be obtained using the 'get_fig()' method, allowing for further plotly operations.
        - Only use keyword arguments throughout.
        
    Examples:
        >>> (ds.px_Plot(df=df_sim_obs,
                        x='dttm',
                        y='value')
                .add_scatter(size_value=2,
                             color_value='black',
                             legend_show=True,
                             legend_name='points')
                .add_trendline(color_value='black',
                               trendline='lowess',
                               lowess_frac=0.2)
                .add_line(color='type',
                          width_value=0.5,
                          color_discrete_map={'sim': 'red',
                                              'obs': 'blue'})
                .label(x='Date',
                       x_tickformat='%b-%d',
                       y='Flow (cfs)',
                       title='Flow for Event')
                .legend(title='Type',
                        x_anchor='right',
                        y_anchor='top',
                        x=1,
                        y=1)
                .layout(margins=[60,10,40,10])
                .write_image('Image.png',
                             width=800,
                             height=600)
                .write_html('Webpage',
                            width='500px')
                .show()
            )
    '''
    fig = None
    df = None
    facet_flag = False
    facet_row = None
    facet_col = None
    facet_row_spacing = None
    facet_col_spacing = None
    facet_n_col = 0
    category_orders = None
    facet_x_show_labels = False
    facet_y_show_labels = False
    facet_x_free = False
    facet_y_free = False
    marginal_x = None
    marginal_y = None
    marginal_xy = None
    x_log = False
    y_log = False

    def __init__(self,
                 df: pd.DataFrame=None,
                 x: str=None,
                 y: str=None) -> None:
        '''Initialize plotly object.

        Args:
            df (pd.DataFrame, optional): Dataframe. Defaults to None.
            x (str, optional): Name of 'x' column. Defaults to None.
            y (str, optional): Name of 'y' column. Defaults to None.

        Notes:
        
            - Any subsequent traces added using 'add_*()' will use these arguments ('df', 'x', 'y') if not specified. If specified, they will be overridden.
        '''
        # fig = px.scatter()

        if df is not None:
            self.df = df.copy()
        self.x = x
        self.y = y
        # self.fig = fig

    def facet(self,
              row: str=None,
              col: str=None,
              row_spacing: float=None,
              col_spacing: float=None,
              n_col: int=None,
              x_show_labels: bool=False,
              y_show_labels: bool=False,
              x_free: bool=False,
              y_free: bool=False,
              row_order: list=None,
              col_order: list=None) -> Self:
        '''Add faceting. Has to be applied before any 'add_*' method is applied.

        Args:
            row (str, optional): Name of row to add row facets. Defaults to None. Updates 'facet_row' in plotly express plots.
            col (str, optional): Name of column to add row facets. Defaults to None. . Updates 'facet_col' in plotly express plots
            row_spacing (flaot, optional): Row spacing. Defaults to None. Updates 'facet_row_spacing' in plotly express plots.
            col_spacing (float, optional): Column spacing. Defaults to None. Updates 'facet_col_spacing' in plotly express plots
            n_col (int, optional): Number of columns if only one of 'row' or 'col' is specified. Defaults to None. Updates 'facet_col_wrap' in plotly express plots
            x_show_labels (bool, optional): Show individual labels for all x-axes. Is set to on if 'x_free' is True. Defaults to False. Updates 'showticklabels' in 'update_xaxes()'.
            y_show_labels (bool, optional): Show individual labels for all y-axes. Is set to on if 'y_free' is True. Defaults to False. Updates 'showticklabels' in 'update_yaxes()'.
            x_free (bool, optional): If x-axis values should be unmatched (be based on individual axis ranges). Defaults to False.
            y_free (bool, optional): If y-axis values should be unmatched (be based on individual axis ranges). Defaults to False.
            row_order (list, optional): List specifying order of values in 'row' column. Defaults to None. Updates 'category_orders' in plotly express plots (by creating a dictionary).
            col_order (list, optional): List specifying order of values in 'col' column. Defaults to None. Updates 'category_orders' in plotly express plots (by creating a dictionary).

        Returns:
            Self: Self object.

        Notes:
            - If only one of 'row' or 'col' is applied, then 'n_col' needs to be specified. Also it doesn't matter if 'row' or 'col' is specified, it is taken as 'col'.
        '''
        if row_order is not None:
            row_order = {row: row_order}
        else:
            row_order = {}
        if col_order is not None:
            col_order = {col: col_order}
        else:
            col_order = {}
        category_orders = row_order | col_order

        if x_free == True:
            x_show_labels = True
        if y_free == True:
            y_show_labels = True

        if row is not None and col is None:
            row, col = None, row

        self.facet_flag=True
        self.facet_row=row
        self.facet_col=col
        self.facet_row_spacing=row_spacing
        self.facet_col_spacing=col_spacing
        self.facet_n_col=n_col
        self.category_orders = category_orders
        self.facet_x_show_labels = x_show_labels
        self.facet_y_show_labels = y_show_labels
        self.facet_x_free = x_free
        self.facet_y_free = y_free

        return self

    def marginal(self,
                 x: str=None,
                 y: str=None) -> Self:
        '''Add marginal plots. Has to be applied before any 'add_*' method is applied.

        Args:
            x (str, optional): Type of plot in x-axis. Defaults to None. Updates 'marginal_x' (or 'marginal') in plotly express plots.
            y (str, optional): Type of plot in y-axis. Defaults to None. Updates 'marginal_y' (or 'marginal') in plotly express plots.

        Returns:
            Self: Self object.

        Notes:
            - For plots where only single axis marginal plot is possible, 'x' is used if it is not None, otherwise 'y' is used.
        '''
        marginal_xy=x if x is not None else y

        self.marginal_x = x
        self.marginal_y = y
        self.marginal_xy = marginal_xy

        return self

    def transform(self,
                  x_log: bool= False,
                  y_log: bool= False) -> Self:
        '''Add log-transformation to x- or y-axis values. Has to be applied before any 'add_*' method is applied.

        Args:
            x_log (bool, optional): Add log-transformation to x-axis values. Defaults to False. Updates 'log_x' in plotly express plots.
            y_log (bool, optional): Add log-transformation to x-axis values. Defaults to False. Updates 'log_y' in plotly express plots.

        Returns:
            Self: Self object.
        '''
        self.x_log = x_log
        self.y_log = y_log

        return self

    def _update_facet_axes(self):
        if self.facet_flag:
            if self.facet_x_show_labels:
                self.fig.update_xaxes(showticklabels=True)
            if self.facet_y_show_labels:
                self.fig.update_yaxes(showticklabels=True)
            if self.facet_x_free:
                self.fig.update_xaxes(matches=None)
            if self.facet_y_free:
                self.fig.update_yaxes(matches=None)

    def _update_legend_show(self, trace, legend_show, legend_name):
        if legend_show is not None:
            trace.update_traces(showlegend=legend_show)
        if legend_name is not None:
            trace.update_traces(name=legend_name)

    def _dec_add(marginal='xy'):
        '''Decorator to make the following updates:
            - Dataframe, x, and y arguments
            - Log scale arguments
            - Category order arguments
            - Facet arguments
            - Marginal arguemnts
            - Hover arguemnts
        '''
        def inner(func):
            def wrapper(self, *args, **kwargs):
                # kwargs = combine_arguments(func, [0, *args], kwargs)
                # kwargs.pop('self')

                if kwargs.get('category_orders') is not None or self.category_orders is not None:
                    kwargs['category_orders'] = ({} if kwargs.get('category_orders') is None else kwargs.get('category_orders')) | ({} if self.category_orders is None else self.category_orders)
                else:
                    kwargs['category_orders'] = self.category_orders

                kwargs['facet_row'] = self.facet_row
                kwargs['facet_col'] = self.facet_col
                kwargs['facet_col_wrap'] = self.facet_n_col
                kwargs['facet_row_spacing'] = self.facet_row_spacing
                kwargs['facet_col_spacing'] = self.facet_col_spacing
                kwargs['log_x'] = self.x_log
                kwargs['log_y'] = self.y_log

                kwargs |= {d.replace('aes_', ''):kwargs[d] for d in kwargs if d.startswith('aes_')}

                _ = dict()

                if kwargs.get('df') is None:
                    if self.df is None:
                        _['data_frame'] = None
                    else:
                        _['data_frame'] = self.df.copy()
                elif 'df' in kwargs:
                    _['data_frame'] = kwargs.pop('df')
                if kwargs.get('x') is None:
                    _['x'] = self.x
                elif 'x' in kwargs:
                    _['x'] = kwargs.pop('x')
                if kwargs.get('y') is None:
                    _['y'] = self.y
                elif 'y' in kwargs:
                    _['y'] = kwargs.pop('y')

                if kwargs.get('x_value') is not None:
                    _['x_value'] = kwargs.pop('x_value')
                if kwargs.get('y_value') is not None:
                    _['y_value'] = kwargs.pop('y_value')

                for name in ['category_orders', 'hover_name', 'hover_data', 'animation_frame', 'animation_group']:
                    if name in kwargs:
                        _[name] = kwargs.pop(name)

                kwargs['_'] = _

                if marginal == 'xy':
                    kwargs['marginal_x'] = self.marginal_x
                    kwargs['marginal_y'] = self.marginal_y
                elif marginal == '':
                    pass
                else:
                    kwargs['marginal']=self.marginal_xy

                kwargs = {k:v for k,v in kwargs.items() if v is not None}

                # kwargs |= _
                # return func(self, *args, **kwargs)

                trace = func(self, *args, **kwargs)
                # trace = func(self, **kwargs)

                self._update_legend_show(trace, kwargs.get('legend_show'), kwargs.get('legend_name'))

                self.add(trace)

                self._update_facet_axes()

                return self

            return wrapper
        return inner

    def add(self,
            trace) -> Self:
        '''Add plotly trace. Can be used to add any trace including traces that have not been implemented using 'add_*()'.

        Args:
            trace (Plotly trace): Plotly trace to add.

        Returns:
            Self: Self object.

        Examples:
            >>> (ds.px_Plot()
                    .add(px.scatter(df_iris,
                                    x='sepal_length',
                                    y='sepal_width')
                                    .update_traces(marker_color='red'))
                    .add(px.scatter(df_iris,
                                    x='petal_length',
                                    y='petal_width')
                                    .update_traces(marker_color='blue'))
                    .show()
                )

        Notes:
            - Traces added this way will not respect 'facet()', 'marginal()', and 'transform()'. This will need to be specified within the added trace.
        '''
        fig = self.fig

        fig = px_add_trace_data(fig, trace)

        self.fig=fig
        return self

    @_dec_add(marginal='xy')
    def add_scatter(self,
                    df: pd.DataFrame = None,
                    x = None,
                    y = None,
                    color = None,
                    size = None,
                    symbol = None,
                    opacity = None,
                    color_value = None,
                    size_value = None,
                    symbol_value = None,
                    color_line_value = None,
                    width_line_value = None,
                    opacity_value = None,
                    aes_color_discrete_sequence = None,
                    aes_color_discrete_map = None,
                    aes_color_continuous_scale = None,
                    aes_range_color = None,
                    aes_color_continuous_midpoint = None,
                    aes_symbol_sequence = None,
                    aes_symbol_map = None,
                    aes_size_max = None,
                    text = None,
                    text_position: Literal['top left', 'top center', 'top right',
                                           'middle left', 'middle center', 'middle right',
                                           'bottom left', 'bottom center', 'bottom right'] = None,
                    category_orders = None,
                    legend_show = None,
                    legend_name = None,
                    hover_name = None,
                    hover_data = None,
                    hover_template = None,
                    animation_frame = None,
                    animation_group = None,
                    _ = None,
                    **kwargs) -> Self:
        trace = \
        (px.scatter(
            color=color,
            size=size,
            symbol=symbol,
            opacity=opacity,
            text=text,
            **_,
            **kwargs
            )
            .update_traces(marker_line_color=color_line_value,
                           marker_line_width=width_line_value)
        )
        if kwargs.get('marginal_x') is None and kwargs.get('marginal_y') is None:
            trace.update_traces(textposition=text_position)
        if color_value is not None:
            trace.update_traces(marker_color=color_value)
        if size_value is not None:
            trace.update_traces(marker_size=size_value)
        if symbol_value is not None:
            trace.update_traces(marker_symbol=symbol_value)
        if opacity_value is not None:
            trace.update_traces(marker_opacity=opacity_value)
        if hover_template is not None:
            trace.update_traces(hovertemplate=hover_template)

        return trace

    @_dec_add(marginal='')
    def add_trendline(self,
                      df: pd.DataFrame = None,
                      x = None,
                      y = None,
                      trendline: Literal['ols', 'lowess', 'rolling', 'ewm', 'expanding'] = None,
                      ols_log_x: bool = False,
                      ols_log_y: bool = False,
                      ols_add_constant: bool = True,
                      lowess_frac: float = 0.6666666,
                      expanding_function: Literal['mean', 'median', 'max', 'min'] = None,
                      expanding_min_periods: int = 1,
                      expanding_axis: Literal[0, 1] = 0,
                      ewm_function: Literal['mean', 'median', 'max', 'min'] = None,
                      ewm_com = None,
                      ewm_span = None,
                      ewm_halflife = None,
                      ewm_alpha = None,
                      ewm_min_periods: int = 0,
                      ewm_adjust = True,
                      ewm_ignore_na = False,
                      ewm_axis: Literal[0, 1] = 0,
                      rolling_function: Literal['mean', 'median', 'max', 'min'] = None,
                      rolling_window = None,
                      rolling_min_periods: int = None,
                      rolling_center = False,
                      rolling_win_type: str = None,
                      rolling_on: str = None,
                      rolling_closed: Literal['right', 'left', 'both', 'neither'] = 'right',
                      rolling_step: int = None,
                      color = None,
                      color_value = None,
                      category_orders = None,
                      legend_show = None,
                      legend_name = None,
                      hover_name = None,
                      hover_data = None,
                      hover_template = None,
                      animation_frame = None,
                      animation_group = None,
                      _ = None,
                      **kwargs) -> Self:
        match trendline:
            case "ols":
                trendline_options = dict(log_x=ols_log_x, log_y=ols_log_y, add_constant=ols_add_constant)
            case "lowess":
                trendline_options = dict(frac=lowess_frac)
            case "expanding":
                trendline_options = dict(function=expanding_function, min_periods=expanding_min_periods, axis=expanding_axis)
            case "ewm":
                trendline_options = dict(function=ewm_function, com=ewm_com, span=ewm_span, halflife=ewm_halflife, alpha=ewm_alpha, min_periods=ewm_min_periods, adjust=ewm_adjust, ignore_na=ewm_ignore_na, axis=ewm_axis)
            case "rolling":
                trendline_options = dict(function=rolling_function, window=rolling_window, min_periods=rolling_min_periods, center=rolling_center, win_type=rolling_win_type, on=rolling_on, closed=rolling_closed, step=rolling_step)
        
        trace = \
        (px.scatter(
            trendline=trendline,
            trendline_options=trendline_options,
            color=color,
            trendline_color_override=color_value,
            **_,
            **kwargs
            )
        )

        trace.data = [t for t in trace.data if t.mode == "lines"]

        return trace

    @_dec_add(marginal='')
    def add_line(self,
                 df: pd.DataFrame = None,
                 x = None,
                 y = None,
                 color = None,
                 dash = None,
                 color_value = None,
                 width_value = None,
                 shape_value = None,
                 dash_value: Literal['dash', 'dot', 'dashdot'] = None,
                 opacity_value = None,
                 aes_color_discrete_sequence = None,
                 aes_color_discrete_map = None,
                 line_dash_sequence = None,
                 line_dash_map = None,
                 symbol_sequence = None,
                 symbol_map = None,
                 text = None,
                 text_position: Literal['top left', 'top center', 'top right',
                                        'middle left', 'middle center', 'middle right',
                                        'bottom left', 'bottom center', 'bottom right'] = None,
                 category_orders = None,
                 legend_show = None,
                 legend_name = None,
                 hover_name = None,
                 hover_data = None,
                 hover_template = None,
                 animation_frame = None,
                 animation_group = None,
                 _ = None,
                 **kwargs) -> Self:
        trace = \
        (px.line(
            color=color,
            line_dash=dash,
            text=text,
            **_,
            **kwargs
            )
            .update_traces(line_width=width_value,
                           line_shape=shape_value,
                           opacity=opacity_value,
                           textposition=text_position)
        )
        if color_value is not None:
            trace.update_traces(line_color=color_value)
        if dash_value is not None:
            trace.update_traces(line_dash=dash_value)
        if hover_template is not None:
            trace.update_traces(hovertemplate=hover_template)

        return trace

    # @_dec_add(marginal='')
    def add_line_hv(self, 
                    x_value = None,
                    y_value = None,
                    # slope_value = None,
                    # color = None,
                    # dash = None,
                    color_value = None,
                    width_value = None,
                    # shape_value = None,
                    dash_value: Literal['dash', 'dot', 'dashdot'] = None,
                    opacity_value = None,
                    # aes_color_discrete_sequence = None,
                    # aes_color_discrete_map = None,
                    # line_dash_sequence = None,
                    # line_dash_map = None,
                    # symbol_sequence = None,
                    # symbol_map = None,
                    text = None,
                    text_position: Literal['top left', 'top right',
                                            'bottom left', 'bottom right'] = None,
                    row='all',
                    col='all',
                    # category_orders = None,
                    # legend_show = None,
                    # legend_name = None,
                    # hover_name = None,
                    # hover_data = None,
                    # hover_template = None,
                    # animation_frame = None,
                    # animation_group = None,
                    # _ = None,
                    **kwargs):
        # Doesn't work if added before other add traces (when there are facets)
        fig = self.fig

        if fig is None:
            fig = px.scatter()
            # self.add_scatter()
            # fig = self.fig

        kwargs['line_width'] = width_value
        kwargs['line_dash'] = dash_value
        kwargs['line_color'] = color_value
        kwargs['opacity'] = opacity_value
        if text is not None:
            kwargs['annotation_text'] = text
            kwargs['annotation_position'] = text_position
        kwargs['row'] = row
        kwargs['col'] = col

        if x_value is not None and y_value is None:
            fig.add_vline(x = x_value, **kwargs)
        elif x_value is None and y_value is not None:
            fig.add_hline(y = y_value, **kwargs)
        self.fig=fig
        return self

    @_dec_add(marginal='')
    def add_bar(self,
                 df: pd.DataFrame = None,
                 x = None,
                 y = None,
                 color = None,
                 pattern = None,
                 color_value = None,
                 color_line_value = None,
                 width_line_value = None,
                 opacity_value = None,
                 aes_color_discrete_sequence = None,
                 aes_color_discrete_map = None,
                 aes_pattern_shape_sequence = None,
                 aes_pattern_shape_map = None,
                 aes_range_color = None,
                 aes_color_continuous_midpoint = None,
                 bar_mode: Literal['group', 'overlay', 'relative'] = 'relative',
                 bar_gap = None,
                 text = None,
                 text_position: Literal['top left', 'top center', 'top right',
                                        'middle left', 'middle center', 'middle right',
                                        'bottom left', 'bottom center', 'bottom right'] = None,
                 category_orders = None,
                 legend_show = None,
                 legend_name = None,
                 hover_name = None,
                 hover_data = None,
                 hover_template = None,
                 animation_frame = None,
                 animation_group = None,
                 _ = None,
                 **kwargs) -> Self:
        if df is None:
            df = self.df.copy()
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        trace = \
        (px.bar(
            color=color,
            pattern_shape=pattern,
            barmode=bar_mode,
            text=text,
            **_,
            **kwargs
            )
            .update_traces(marker_line_color=color_line_value,
                           marker_line_width=width_line_value,
                           textposition=text_position)
            .update_layout(bargap=bar_gap)
        )
        if color_value is not None:
            trace.update_traces(marker_color=color_value)
        if opacity_value is not None:
            trace.update_traces(marker_opacity=opacity_value)
        if hover_template is not None:
            trace.update_traces(hovertemplate=hover_template)

        return trace

    @_dec_add(marginal='x')
    def add_histogram(self,
                      df: pd.DataFrame = None,
                      x = None,
                      y = None,
                      color = None,
                      shape = None,
                      color_value = None,
                      color_line_value = None,
                      width_line_value = None,
                      opacity_value = None,
                      aes_color_discrete_sequence = None,
                      aes_color_discrete_map = None,
                      aes_pattern_shape_sequence = None,
                      aes_pattern_shape_map = None,
                      text_auto = False,
                      bins_n = None,
                      bins_start = None,
                      bins_end = None,
                      bins_size = None,
                      cumulative = False,
                      hist_func: Literal['count', 'sum', 'avg', 'min', 'max'] = None,
                      hist_norm: Literal['percent', 'probability', 'density', 'probability density'] = None,
                      bar_mode: Literal['group', 'overlay', 'relative'] = 'relative',
                      bar_norm: Literal['fraction', 'percent'] = None,
                      bar_gap = None,
                      category_orders = None,
                      legend_show = None,
                      legend_name = None,
                      hover_name = None,
                      hover_data = None,
                      hover_template = None,
                      animation_frame = None,
                      animation_group = None,
                      _ = None,
                      **kwargs) -> Self:
        if hist_func is None:
            hist_func = 'count' if y is None else 'sum'

        trace = \
        (px.histogram(
            color=color,
            pattern_shape=shape,
            text_auto=text_auto,
            nbins=bins_n,
            cumulative=cumulative,
            histfunc=hist_func,
            histnorm=hist_norm,
            barmode=bar_mode,
            barnorm=bar_norm,
            **_,
            **kwargs
            )
            .update_traces(marker_line_color=color_line_value,
                           marker_line_width=width_line_value)
            .update_layout(bargap=bar_gap)
        )
        if kwargs.get('marginal') is None: # Is this a plotly express bug?
            trace.update_traces(xbins = dict(start = bins_start,
                                             end = bins_end,
                                             size = bins_size))

        if color_value is not None:
            trace.update_traces(marker_color=color_value)
        if opacity_value is not None:
            trace.update_traces(marker_opacity=opacity_value)
        if hover_template is not None:
            trace.update_traces(hovertemplate=hover_template)

        return trace

    @_dec_add(marginal='xy')
    def add_heatmap(self,
                    df: pd.DataFrame = None,
                    x = None,
                    y = None,
                    z = None,
                    opacity_value = None,
                    aes_color_continuous_scale = None,
                    aes_range_color = None,
                    color_continuous_midpoint = None,
                    text_auto = False,
                    bins_n_x = None,
                    bins_start_x = None,
                    bins_end_x = None,
                    bins_size_x = None,
                    bins_n_y = None,
                    bins_start_y = None,
                    bins_end_y = None,
                    bins_size_y = None,
                    hist_func: Literal['count', 'sum', 'avg', 'min', 'max'] = None,
                    hist_norm: Literal['percent', 'probability', 'density', 'probability density'] = None,
                    bar_mode: Literal['group', 'overlay', 'relative'] = 'relative',
                    bar_norm: Literal['fraction', 'percent'] = None,
                    bar_gap = None,
                    category_orders = None,
                    legend_show = None,
                    legend_name = None,
                    hover_name = None,
                    hover_data = None,
                    hover_template = None,
                    animation_frame = None,
                    animation_group = None,
                    _ = None,
                    **kwargs) -> Self:
        if hist_func is None:
            hist_func = 'count' if z is None else 'sum'

        trace = \
        (px.density_heatmap(
            z=z,
            text_auto=text_auto,
            nbinsx=bins_n_x,
            nbinsy=bins_n_y,
            histfunc=hist_func,
            histnorm=hist_norm,
            **_,
            **kwargs
            )
        )
        if kwargs.get('marginal_x') is None and kwargs.get('marginal_y') is None: # Is this a plotly express bug?
            trace.update_traces(xbins = dict(start = bins_start_x,
                                             end = bins_end_x,
                                             size = bins_size_x),
                                ybins = dict(start = bins_start_y,
                                             end = bins_end_y,
                                             size = bins_size_y))

        if opacity_value is not None:
            trace.update_traces(marker_opacity=opacity_value)
        if hover_template is not None:
            trace.update_traces(hovertemplate=hover_template)

        return trace

    #TODO facet
    def add_kde(self,
                df: pd.DataFrame = None,
                x = None,
                color_value = None,
                width_value = None,
                dash_value: Literal['dash', 'dot', 'dashdot'] = None,
                legend_show = None,
                legend_name = None):
        facet_row=self.facet_row
        facet_col=self.facet_col
        facet_row_spacing=self.facet_row_spacing
        facet_col_spacing=self.facet_col_spacing
        facet_n_col=self.facet_n_col
        category_orders=self.category_orders
        x_log=self.x_log
        y_log=self.y_log

        if df is None:
            df = self.df.copy()
        if x is None:
            x = self.x

        trace = \
        (ff.create_distplot([df[x].tolist()],
                               [x],
                               show_hist=False,
                               show_rug=False)
            .update_traces(line_color=color_value,
                           line_width=width_value,
                           line_dash=dash_value)
            .update_traces(showlegend=False)
        )

        self._update_legend_show(trace, legend_show, legend_name)

        self.add(trace)

        self._update_facet_axes()

        return self

    def label(self,
              x: str= None,
              y: str= None,
              title: str= None,
              x_tickformat: str= None,
              y_tickformat: str= None,
              title_x_just: float= None) -> Self:
        '''Add axis labels.

        Args:
            x (str, optional): x-axis label. Defaults to None. Updates 'xaxis_title' in 'update_layout()'.
            y (str, optional): y-axis label. Defaults to None. Updates 'yaxis_title' in 'update_layout()'.
            title (str, optional): Plot title. Defaults to None. Updates 'title' in 'update_layout()'.
            x_tickformat (str, optional): x-axis label format. Defaults to None. Updates 'tickformat' in 'update_xaxes()'.
            y_tickformat (str, optional): y-axis label format. Defaults to None. Updates 'tickformat' in 'update_yaxes()'.
            title_x_just (float, optional): Sets x position of title in normalized coordinates, with 0 being left and 1 being right. Defaults to None. Updates 'title_x' in 'update_layout()'.

        Returns:
            Self: _description_

        Notes:
            - For tick format, tick label formatting rule uses d3 formatting mini-languages which are very similar to those in Python. For numbers, see: https://github.com/d3/d3-format/tree/v1.4.5#d3-format. And for dates see: https://github.com/d3/d3-time-format/tree/v2.2.3#locale_format. We add two items to d3's date formatter: "%h" for half of the year as a decimal number as well as "%{n}f" for fractional seconds with n digits. For example, "2016-10-13 09:15:23.456" with tickformat "%H~%M~%S.%2f" would display "09~15~23.46".
        '''
        fig = self.fig

        fig.update_layout(xaxis_title = x,
                          yaxis_title = y,
                          title = title)

        fig.update_xaxes(tickformat=x_tickformat)
        fig.update_yaxes(tickformat=y_tickformat)
        fig.update_layout(title_x=title_x_just)

        return self

    def legend(self,
               show: bool= True,
               title: bool= None,
               x_anchor: Literal['auto', 'left', 'center', 'right'] = None,
               y_anchor: Literal['auto', 'top', 'middle', 'bottom'] = None,
               x: float= None,
               y: float= None,
               orientation: Literal['h', 'v']= None) -> Self:
        '''Update legend properties.

        Args:
            show (bool, optional): Whether to show legend. Defaults to True. Updates 'showlegend' in 'update_layout()'.
            title (bool, optional): Legend title. Defaults to None. Updates 'legend_title' in 'update_layout()'.
            x_anchor (Literal[&#39;auto&#39;, &#39;left&#39;, &#39;center&#39;, &#39;right&#39;], optional): Sets the legend's horizontal position anchor. Defaults to None. Updates 'legend_xanchor' in 'update_layout()'.
            y_anchor (Literal[&#39;auto&#39;, &#39;top&#39;, &#39;middle&#39;, &#39;bottom&#39;], optional): Sets the legend's vertical position anchor. Defaults to None. Updates 'legend_yanchor' in 'update_layout()'.
            x (float, optional): Sets x-position in normalized units. Defaults to None. Updates 'legend_x' in 'update_layout()'.
            y (float, optional): Sets y-position in normalized units. Defaults to None. Updates 'legend_y' in 'update_layout()'.
            orientation (Literal[&#39;h&#39;, &#39;v&#39;], optional): Sets legend orientation. Defaults to None. Updates 'legend_orientation' in 'update_layout()'.

        Returns:
            Self: Self object.

        Note:
            - Current implementation uses only 'paper' ref. May support 'container' ref in the future.
        '''
        fig = self.fig

        fig.update_layout(showlegend = show,
                          legend = dict(title=title,
                                        xanchor=x_anchor,
                                        yanchor=y_anchor,
                                        x = x,
                                        y = y,
                                        orientation = orientation))

        return self

    def colorbar(self,
                 show: bool= True,
                 title: str= None,
                 x_anchor: Literal['left', 'center', 'right'] = None,
                 y_anchor: Literal['top', 'middle', 'bottom'] = None,
                 x: float= None,
                 y: float= None,
                 orientation: Literal['h', 'v']= None,
                 thickness: float= None,
                 len: float= 1) -> Self:
        '''Update color bar legend.

        Args:
            show (bool, optional): Whether to show legend. Defaults to True. Updates 'showlegend' in 'update_layout()'.
            title (str, optional): Color bar title. Defaults to None. Updates 'colorbar_title' in 'update_coloraxes()'.
            x_anchor (Literal[&#39;left&#39;, &#39;center&#39;, &#39;right&#39;], optional): Sets the legend's horizontal position anchor. Defaults to None. Updates 'colorbar_xanchor' in 'update_coloraxes()'.
            y_anchor (Literal[&#39;top&#39;, &#39;middle&#39;, &#39;bottom&#39;], optional): Sets the legend's vertical position anchor. Defaults to None. Updates 'colorbar_yanchor' in 'update_coloraxes()'.
            x (float, optional): Sets x-position in normalized units. Defaults to None. Updates 'colorbar_x' in 'update_coloraxes()'.
            y (float, optional): Sets y-position in normalized units. Defaults to None. Updates 'colorbar_y' in 'update_coloraxes()'.
            orientation (Literal[&#39;h&#39;, &#39;v&#39;], optional): Sets legend orientation. Defaults to None. Updates 'colorbar_orientation' in 'update_coloraxes()'.
            thickness (float, optional): Sets the thickness of the color bar This measure excludes the size of the padding, ticks and labels. Defaults to None. Updates 'colorbar_thickness' in 'update_coloraxes()'.
            len (float, optional): Sets the length of the color bar. This measure excludes the padding of both ends. That is, the color bar length is this length minus the padding on both ends. Defaults to 1. Updates 'colorbar_len' in 'update_coloraxes()'.

        Returns:
            Self: Self object.
        '''
        fig = self.fig

        fig.update_layout(showlegend = show)
        fig.update_coloraxes(dict(colorbar_title=title,
                                  colorbar_xanchor=x_anchor,
                                  colorbar_yanchor=y_anchor,
                                  colorbar_x = x,
                                  colorbar_y = y,
                                  colorbar_orientation = orientation,
                                  colorbar_thickness=thickness,
                                  colorbar_len=len))
        # fig.update_layout(showlegend = show,
        #                   coloraxis_colorbar=dict(title=title,
        #                                           xanchor=x_anchor,
        #                                           yanchor=y_anchor,
        #                                           x = x,
        #                                           y = y,
        #                                           orientation = orientation,
        #                                           thickness=thickness,
        #                                           len=len))

        return self

    def size(self,
             width: float=None,
             height: float=None) -> Self:
        '''Set plot dimensions.

        Args:
            width (float, optional): Set plot's width (in px). Defaults to None. Updates 'width' in 'update_layout()'.
            height (float, optional): Set plot's height (in px). Defaults to None. Updates 'height' in 'update_layout()'.

        Returns:
            Self: Self object.
        '''
        fig = self.fig

        fig.update_layout(width=width,
                          height=height)

        return self

    def _update_axis(self,
                     axis='x',
                     kwargs=None):
        fig = self.fig

        kwargs = dict(showgrid = kwargs['tick_show_grid'],
                      zeroline = kwargs['tick_show_zero_line'],
                      showticklabels = kwargs['tick_show_labels'],
                      tick0 = kwargs['tick_0'],
                      dtick = kwargs['tick_del'],
                      ticklabelstep = kwargs['tick_label_step'],
                      nticks = kwargs['tick_n'],
                      tickangle = kwargs['tick_angle'],
                      minor_showgrid = kwargs['minor_tick_show_grid'],
                      minor_tickcolor = kwargs['minor_tick_color'],
                      minor_ticklen = kwargs['minor_tick_len'],
                      minor_griddash = kwargs['minor_tick_dash'],
                      showline = kwargs['border_show'],
                      linewidth = kwargs['border_width'],
                      linecolor = kwargs['border_color'],
                      mirror = kwargs['border_mirror'],
                      range = kwargs['value_range'],
                      categoryorder = kwargs.get('category_order'),
                      autorange = None if kwargs['value_rev'] is None else 'reversed')

        kwargs = {k:v for k,v in kwargs.items() if v is not None}

        if axis=='x':
            fig.update_xaxes(**kwargs)
        elif axis=='y':
            fig.update_yaxes(**kwargs)
        else:
            fig.update_xaxes(**kwargs)
            fig.update_yaxes(**kwargs)

    def axis(self,
             tick_show_grid: bool=None,
             tick_show_zero_line: bool=None,
             tick_show_labels: bool=None,
             tick_0: float=None,
             tick_del: float=None,
             tick_label_step: int=None,
             tick_n: int=None,
             tick_angle: float=None,
             minor_tick_show_grid: float=None,
             minor_tick_color: str=None,
             minor_tick_len: float=None,
             minor_tick_dash: str=None,
             border_show: bool=None,
             border_width: float=None,
             border_color: str=None,
             border_mirror: Literal[True, False, "ticks", "all", "allticks"]=None,
             value_range: list=None,
             value_rev: bool=None,
             category_order: dict=None,
             aspect_ratio: float=None):
        '''Update x-axis properties.

        Args:
            tick_show_grid (bool, optional): Determines whether or not grid lines are drawn. If "True", the grid lines are drawn at every tick mark. Defaults to None. Updates 'showgrid' in 'update_xaxes()' and 'update_yaxes()'.
            tick_show_zero_line (bool, optional): Determines whether or not a line is drawn at along the 0 value of this axis. If "True", the zero line is drawn on top of the grid lines. Defaults to None. Updates 'zeroline' in 'update_xaxes()' and 'update_yaxes()'.
            tick_show_labels (bool, optional): Determines whether or not the tick labels are drawn. Defaults to None (True). Updates 'showticklabels' in 'update_xaxes()' and 'update_yaxes()'.
            tick_0 (float, optional): Sets the placement of the first tick on this axis. Use with `dtick`. Defaults to None. Updates 'tick0' in 'update_xaxes()' and 'update_yaxes()'.
            tick_del (float, optional): Sets the step in-between ticks on this axis. Use with `tick0`. Defaults to None. Updates 'dtick' in 'update_xaxes()' and 'update_yaxes()'.
            tick_label_step (int, optional): Sets the spacing between tick labels as compared to the spacing between ticks. A value of 1 (default) means each tick gets a label. A value of 2 means shows every 2nd label. A larger value n means only every nth tick is labeled. `tick0` determines which labels are shown. Defaults to None. Updates 'ticklabelstep' in 'update_xaxes()' and 'update_yaxes()'.
            tick_n (int, optional): Specifies the maximum number of ticks for the particular axis. The actual number of ticks will be chosen automatically to be less than or equal to `nticks`. Defaults to None. Updates 'nticks' in 'update_xaxes()' and 'update_yaxes()'.
            tick_angle (float, optional): Sets the angle of the tick labels with respect to the horizontal. For example, a `tickangle` of -90 draws the tick labels vertically. Defaults to None. Updates 'tickangle' in 'update_xaxes()' and 'update_yaxes()'.
            minor_tick_show_grid (float, optional): Determines whether or not minor grid lines are drawn. If "True", the grid lines are drawn at every tick mark.. Defaults to None. Updates 'minor_showgrid' in 'update_xaxes()' and 'update_yaxes()'.
            minor_tick_color (str, optional): Sets the minor tick color. Defaults to None. Updates 'minor_tickcolor' in 'update_xaxes()' and 'update_yaxes()'.
            minor_tick_len (float, optional): Sets the minor tick length (in px).. Defaults to None. Updates 'minor_ticklen' in 'update_xaxes()' and 'update_yaxes()'.
            minor_tick_dash (str, optional): Sets the dash style of lines. Set to a dash type string ("solid", "dot", "dash", "longdash", "dashdot", or "longdashdot") or a dash length list in px (eg "5px,10px,2px,2px"). Defaults to None. Updates 'minor_griddash' in 'update_xaxes()' and 'update_yaxes()'.
            border_show (bool, optional): Determines whether or not a line bounding this axis is drawn. Defaults to None. Updates 'showline' in 'update_xaxes()' and 'update_yaxes()'.
            border_width (float, optional): Sets the width (in px) of the axis line. Defaults to None (1). Updates 'linewidth' in 'update_xaxes()' and 'update_yaxes()'.
            border_color (str, optional): Sets the axis line color. Defaults to None ('#444'). Updates 'linecolor' in 'update_xaxes()' and 'update_yaxes()'.
            border_mirror (Literal[True, False, "ticks", "all", "allticks"], optional): Determines if the axis lines or/and ticks are mirrored to the opposite side of the plotting area. If "True", the axis lines are mirrored. If "ticks", the axis lines and ticks are mirrored. If "False", mirroring is disable. If "all", axis lines are mirrored on all shared-axes subplots. If "allticks", axis lines and ticks are mirrored on all shared-axes subplots. Defaults to None. Updates 'mirror' in 'update_xaxes()' and 'update_yaxes()'.
            value_range (list, optional): Sets the range of this axis. . Defaults to None. Updates 'range' in 'update_xaxes()' and 'update_yaxes()'.
            value_rev (bool, optional): Reverse axis direction. Defaults to None.  Updates 'autorange' in 'update_xaxes()' and 'update_yaxes()' to 'reversed' if this is not None.
            category_order (dict, optional): Dictionary specifying value orders for category variables (key: variable name, value: list of values in order). Defaults to None. Updates 'categoryorder' in 'update_xaxes()' and 'update_yaxes()'.
            aspect_ratio (float, optional): Aspect ratio of axes. Every unit on y-axis spans this value times the number of pixels as a unit on x-axis. Defaults to None. Updates 'scaleratio' and sets 'scaleanchor' to 'x' in 'update_yaxes()'.

        Returns:
            Self: Self Object.
        '''
        self._update_axis('both', locals())
        fig = self.fig

        if aspect_ratio is not None:
            fig.update_yaxes(scaleratio = aspect_ratio,
                             scaleanchor = 'x')

        return self

    def axis_x(self,
               tick_show_grid: bool=None,
               tick_show_zero_line: bool=None,
               tick_show_labels: bool=None,
               tick_0: float=None,
               tick_del: float=None,
               tick_label_step: int=None,
               tick_n: int=None,
               tick_angle: float=None,
               minor_tick_show_grid: float=None,
               minor_tick_color: str=None,
               minor_tick_len: float=None,
               minor_tick_dash: str=None,
               border_show: bool=None,
               border_width: float=None,
               border_color: str=None,
               border_mirror: Literal[True, False, "ticks", "all", "allticks"]=None,
               value_range: list=None,
               value_rev: bool=None,
               category_order: dict=None) -> Self:
        '''Update x-axis properties.

        Args:
            tick_show_grid (bool, optional): Determines whether or not grid lines are drawn. If "True", the grid lines are drawn at every tick mark. Defaults to None. Updates 'showgrid' in 'update_xaxes()'.
            tick_show_zero_line (bool, optional): Determines whether or not a line is drawn at along the 0 value of this axis. If "True", the zero line is drawn on top of the grid lines. Defaults to None. Updates 'zeroline' in 'update_xaxes()'.
            tick_show_labels (bool, optional): Determines whether or not the tick labels are drawn. Defaults to None (True). Updates 'showticklabels' in 'update_xaxes()'.
            tick_0 (float, optional): Sets the placement of the first tick on this axis. Use with `dtick`. Defaults to None. Updates 'tick0' in 'update_xaxes()'.
            tick_del (float, optional): Sets the step in-between ticks on this axis. Use with `tick0`. Defaults to None. Updates 'dtick' in 'update_xaxes()'.
            tick_label_step (int, optional): Sets the spacing between tick labels as compared to the spacing between ticks. A value of 1 (default) means each tick gets a label. A value of 2 means shows every 2nd label. A larger value n means only every nth tick is labeled. `tick0` determines which labels are shown. Defaults to None. Updates 'ticklabelstep' in 'update_xaxes()'.
            tick_n (int, optional): Specifies the maximum number of ticks for the particular axis. The actual number of ticks will be chosen automatically to be less than or equal to `nticks`. Defaults to None. Updates 'nticks' in 'update_xaxes()'.
            tick_angle (float, optional): Sets the angle of the tick labels with respect to the horizontal. For example, a `tickangle` of -90 draws the tick labels vertically. Defaults to None. Updates 'tickangle' in 'update_xaxes()'.
            minor_tick_show_grid (float, optional): Determines whether or not minor grid lines are drawn. If "True", the grid lines are drawn at every tick mark.. Defaults to None. Updates 'minor_showgrid' in 'update_xaxes()'.
            minor_tick_color (str, optional): Sets the minor tick color. Defaults to None. Updates 'minor_tickcolor' in 'update_xaxes()'.
            minor_tick_len (float, optional): Sets the minor tick length (in px).. Defaults to None. Updates 'minor_ticklen' in 'update_xaxes()'.
            minor_tick_dash (str, optional): Sets the dash style of lines. Set to a dash type string ("solid", "dot", "dash", "longdash", "dashdot", or "longdashdot") or a dash length list in px (eg "5px,10px,2px,2px"). Defaults to None. Updates 'minor_griddash' in 'update_xaxes()'.
            border_show (bool, optional): Determines whether or not a line bounding this axis is drawn. Defaults to None. Updates 'showline' in 'update_xaxes()'.
            border_width (float, optional): Sets the width (in px) of the axis line. Defaults to None (1). Updates 'linewidth' in 'update_xaxes()'.
            border_color (str, optional): Sets the axis line color. Defaults to None ('#444'). Updates 'linecolor' in 'update_xaxes()'.
            border_mirror (Literal[True, False, "ticks", "all", "allticks"], optional): Determines if the axis lines or/and ticks are mirrored to the opposite side of the plotting area. If "True", the axis lines are mirrored. If "ticks", the axis lines and ticks are mirrored. If "False", mirroring is disable. If "all", axis lines are mirrored on all shared-axes subplots. If "allticks", axis lines and ticks are mirrored on all shared-axes subplots. Defaults to None. Updates 'mirror' in 'update_xaxes()'.
            value_range (list, optional): Sets the range of this axis. . Defaults to None. Updates 'range' in 'update_xaxes()'.
            value_rev (bool, optional): Reverse axis direction. Defaults to None.  Updates 'autorange' in 'update_xaxes()' to 'reversed' if this is not None.
            category_order (dict, optional): Dictionary specifying value orders for category variables (key: variable name, value: list of values in order). Defaults to None. Updates 'categoryorder' in 'update_xaxes()'.

        Returns:
            Self: Self Object.
        '''
        self._update_axis('x', locals())

        return self

    def axis_y(self,
               tick_show_grid: bool=None,
               tick_show_zero_line: bool=None,
               tick_show_labels: bool=None,
               tick_0: float=None,
               tick_del: float=None,
               tick_label_step: int=None,
               tick_n: int=None,
               tick_angle: float=None,
               minor_tick_show_grid: float=None,
               minor_tick_color: str=None,
               minor_tick_len: float=None,
               minor_tick_dash: str=None,
               border_show: bool=None,
               border_width: float=None,
               border_color: str=None,
               border_mirror: Literal[True, False, "ticks", "all", "allticks"]=None,
               value_range: list=None,
               value_rev: bool=None,
               category_order: dict=None) -> Self:
        '''Update x-axis properties.

        Args:
            tick_show_grid (bool, optional): Determines whether or not grid lines are drawn. If "True", the grid lines are drawn at every tick mark. Defaults to None. Updates 'showgrid' in 'update_yaxes()'.
            tick_show_zero_line (bool, optional): Determines whether or not a line is drawn at along the 0 value of this axis. If "True", the zero line is drawn on top of the grid lines. Defaults to None. Updates 'zeroline' in 'update_yaxes()'.
            tick_show_labels (bool, optional): Determines whether or not the tick labels are drawn. Defaults to None (True). Updates 'showticklabels' in 'update_yaxes()'.
            tick_0 (float, optional): Sets the placement of the first tick on this axis. Use with `dtick`. Defaults to None. Updates 'tick0' in 'update_yaxes()'.
            tick_del (float, optional): Sets the step in-between ticks on this axis. Use with `tick0`. Defaults to None. Updates 'dtick' in 'update_yaxes()'.
            tick_label_step (int, optional): Sets the spacing between tick labels as compared to the spacing between ticks. A value of 1 (default) means each tick gets a label. A value of 2 means shows every 2nd label. A larger value n means only every nth tick is labeled. `tick0` determines which labels are shown. Defaults to None. Updates 'ticklabelstep' in 'update_yaxes()'.
            tick_n (int, optional): Specifies the maximum number of ticks for the particular axis. The actual number of ticks will be chosen automatically to be less than or equal to `nticks`. Defaults to None. Updates 'nticks' in 'update_yaxes()'.
            tick_angle (float, optional): Sets the angle of the tick labels with respect to the horizontal. For example, a `tickangle` of -90 draws the tick labels vertically. Defaults to None. Updates 'tickangle' in 'update_yaxes()'.
            minor_tick_show_grid (float, optional): Determines whether or not minor grid lines are drawn. If "True", the grid lines are drawn at every tick mark.. Defaults to None. Updates 'minor_showgrid' in 'update_yaxes()'.
            minor_tick_color (str, optional): Sets the minor tick color. Defaults to None. Updates 'minor_tickcolor' in 'update_yaxes()'.
            minor_tick_len (float, optional): Sets the minor tick length (in px).. Defaults to None. Updates 'minor_ticklen' in 'update_yaxes()'.
            minor_tick_dash (str, optional): Sets the dash style of lines. Set to a dash type string ("solid", "dot", "dash", "longdash", "dashdot", or "longdashdot") or a dash length list in px (eg "5px,10px,2px,2px"). Defaults to None. Updates 'minor_griddash' in 'update_yaxes()'.
            border_show (bool, optional): Determines whether or not a line bounding this axis is drawn. Defaults to None. Updates 'showline' in 'update_yaxes()'.
            border_width (float, optional): Sets the width (in px) of the axis line. Defaults to None (1). Updates 'linewidth' in 'update_yaxes()'.
            border_color (str, optional): Sets the axis line color. Defaults to None ('#444'). Updates 'linecolor' in 'update_yaxes()'.
            border_mirror (Literal[True, False, "ticks", "all", "allticks"], optional): Determines if the axis lines or/and ticks are mirrored to the opposite side of the plotting area. If "True", the axis lines are mirrored. If "ticks", the axis lines and ticks are mirrored. If "False", mirroring is disable. If "all", axis lines are mirrored on all shared-axes subplots. If "allticks", axis lines and ticks are mirrored on all shared-axes subplots. Defaults to None. Updates 'mirror' in 'update_yaxes()'.
            value_range (list, optional): Sets the range of this axis. . Defaults to None. Updates 'range' in 'update_yaxes()'.
            value_rev (bool, optional): Reverse axis direction. Defaults to None.  Updates 'autorange' in 'update_yaxes()' to 'reversed' if this is not None.
            category_order (dict, optional): Dictionary specifying value orders for category variables (key: variable name, value: list of values in order). Defaults to None. Updates 'categoryorder' in 'update_yaxes()'.

        Returns:
            Self: Self Object.
        '''
        self._update_axis('y', locals())

        return self

    def layout(self,
               margins: dict|list=None,
               margin_l: float= None,
               margin_r: float= None,
               margin_t: float= None,
               margin_b: float= None,
               scatter_mode: Literal['overlay', 'group'] = None,
               scatter_gap: float = None,
               **kwargs) -> Self:
        '''Update layout properties.

        Args:
            margins (dict | list| tuple, optional): Sets margins (in px). If using dictionary, use keys: 'l', 'r', 't', and 'b'. If using list or tuple, use order: l,r,t,b. Defaults to None. Updates 'margin' in 'update_layout()'.
            margin_l (float, optional): Sets the left margin (in px). Defaults to None (80). Updates 'margin_l' in 'update_layout()'.
            margin_r (float, optional): Sets the right margin (in px). Defaults to None (80). Updates 'margin_r' in 'update_layout()'.
            margin_t (float, optional): Sets the top margin (in px). Defaults to None (100). Updates 'margin_t' in 'update_layout()'.
            margin_b (float, optional): Sets the bottom margin (in px). Defaults to None (80). Updates 'margin_b' in 'update_layout()'.
            scatter_mode (Literal[&#39;overlay&#39;, &#39;group&#39;], optional): Determines how scatter points at the same location coordinate are displayed on the graph. With "group", the scatter points are plotted next to one another centered around the shared location. With "overlay", the scatter points are plotted over one another, you might need to reduce "opacity" to see multiple scatter points. Defaults to None ('overlay'). Updates 'scattermode' in 'update_layout()'.
            scatter_gap (float, optional): Sets the gap (in plot fraction) between scatter points of adjacent location coordinates. Defaults to `bargap`. Should be between 0 and 1 (inclusive). Defaults to None. Updates 'scattergap' in 'update_layout()'.
            kwargs: Set any other properties that can go into 'update_layout()'.

        Returns:
            Self: Self object.
        '''
        fig = self.fig

        kwargs = {k:v for k,v in kwargs.items() if v is not None}

        if margins is not None:
            if isinstance(margins, list|tuple):
                margin_l, margin_r, margin_t, margin_b = margins
            else:
                margin_l = margins.get('l')
                margin_r = margins.get('r')
                margin_t = margins.get('t')
                margin_b = margins.get('b')
        fig.update_layout(margin_l=margin_l,
                          margin_r=margin_r,
                          margin_t=margin_t,
                          margin_b=margin_b,
                          scattermode=scatter_mode,
                          scattergap=scatter_gap,
                          **kwargs)

        return self

    def show(self, scroll_zoom=False) -> Self:
        '''Show the plot. Calls 'show()' method of the plotly figure object.

        Returns:
            Self: Self Object.
        '''
        fig = self.fig

        fig.show(config={'scrollZoom': scroll_zoom})

        return self

    def get_fig(self):
        '''Get the plotly figure object.
        '''
        fig = self.fig

        return fig

    def write_image(self,
                    file: str,
                    format: Literal['png', 'jpg', 'jpeg', 'webp', 'svg', 'pdf', 'eps']=None,
                    width: int=None,
                    height: int=None,
                    scale: float=None,
                    *args,
                    **kwargs) -> Self:
        '''Convert a figure to a static image and write it to a file or writeable object.

        Args:
            file (str): A string representing a local file path or a writeable object (e.g. a pathlib.Path object or an open file descriptor).
            format (str, optional): The desired image format. If not specified and file is a string then this will default to the file extension. If not specified and file is not a string then this will default to plotly.io.config.default_format. 'eps' requires the poppler library to be installed. Defaults to None.
            width (int, optional): The width of the exported image in layout pixels. If the scale property is 1.0, this will also be the width of the exported image in physical pixels. If not specified, will default to plotly.io.config.default_width. Defaults to None.
            height (int, optional): The height of the exported image in layout pixels. If the scale property is 1.0, this will also be the height of the exported image in physical pixels. If not specified, will default to plotly.io.config.default_height. Defaults to None.
            scale (float, optional): The scale factor to use when exporting the figure. A scale factor larger than 1.0 will increase the image resolution with respect to the figure's layout pixel dimensions. Whereas as scale factor of less than 1.0 will decrease the image resolution. If not specified, will default to plotly.io.config.default_scale. Defaults to None.

        Returns:
            Self: Self Object.
        '''
        fig = self.fig

        fig.write_image(file, format, width, height, scale, *args, **kwargs)

        return self

    def write_html(self,
                   file: str,
                   width: int | str='100%',
                   height: int | str='100%',
                   *args,
                   **kwargs) -> Self:
        '''Write a figure to an HTML file representation.

        Args:
            file (str): A string representing a local file path or a writeable object (e.g. a pathlib.Path object or an open file descriptor). Adding '.html' at the end is optional.
            width (int | str, optional): The default figure width to use if the provided figure does not specify its own layout.width/layout.height property. May be specified in pixels as an integer (e.g. 500), or as a css width style string (e.g. '500px', '100%'). If not provided, figure takes up the size of the window. Defaults to '100%'.
            height (int | str, optional): The height figure width to use if the provided figure does not specify its own layout.width/layout.height property. May be specified in pixels as an integer (e.g. 500), or as a css width style string (e.g. '500px', '100%'). If not provided, figure takes up the size of the window. Defaults to '100%'.

        Returns:
            Self: Self Object.
        '''
        fig = self.fig

        if not file[-5:] == '.html':
            file = file + '.html'

        fig.write_html(file, default_width=width, default_height=height, *args, **kwargs)

        return self

#endregion -----------------------------------------------------------------------------------------
