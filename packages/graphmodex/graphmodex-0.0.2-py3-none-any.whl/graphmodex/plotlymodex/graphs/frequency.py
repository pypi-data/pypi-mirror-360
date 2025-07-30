import os
import sys
import warnings

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff

from typing import Union, Literal

sys.path.append(os.path.abspath('..'))
from graphmodex import plotlymodex


__all__ = [
    'frequency'
]


def frequency(
        df:pd.DataFrame=None, 
        x:str=None, 
        covariate:str=None, 
        bin_size:Union[int, None]=None, 
        colors:Union[list, str]=None,
        histnorm:Literal[None, 'probability density']='probability density', 
        categorical:bool=None,
        show_curve:bool=True, 
        show_hist:bool=True, 
        show_rug:bool=False, 
        opacity:float=0.8,
        min_max:bool=True, 
        sort_x:bool=True, 
        layout_kwargs:dict=None, 
        bar_kwargs:dict=None, 
        marker_kwargs:dict=None
    ) -> go.Figure:
    """
    Plot the frequency distribution of a column in a DataFrame using Plotly, supporting both categorical and continuous variables.

    This function generates frequency plots for a specified column in a DataFrame. It supports categorical and continuous data types
    and optionally allows stratification by a covariate. For continuous data, distribution plots are shown; for categorical data,
    bar plots are rendered. It uses Plotly for interactive visualization.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing the data.
    x : str
        Column name in `df` for which to calculate the frequency or a list with the values (`df` must not be specified in this case).
    covariate : str, optional
        Column to stratify data by or a list with the values (`df` must not be specified in this case). Cannot be the same as `x`.
    bin_size : int or None, optional
        Bin size for continuous data. If None, it's computed automatically.
    colors : list or str, optional
        List of colors or a single color string for the plot.
    histnorm : {'probability density', None}, default='probability density'
        Normalization type for histogram (used in continuous plots).
    categorical : bool, optional
        Force the column `x` to be treated as categorical.
    show_curve : bool, default=True
        Whether to display KDE curve in continuous plots.
    show_hist : bool, default=True
        Whether to display histogram bars in continuous plots.
    show_rug : bool, default=False
        Whether to show rug plot in continuous plots.
    opacity : float, default=0.8
        Opacity of the plot elements.
    min_max : bool, default=True
        For continuous plots with covariate: include min/max values across all groups in each group.
    sort_x : bool, default=True
        Whether to sort x-axis categories (for categorical plots without covariate).
    layout_kwargs : dict, optional
        Additional keyword arguments passed to the layout function.
    bar_kwargs : dict, optional
        Additional keyword arguments passed to `go.Bar` in categorical plots.
    marker_kwargs : dict, optional
        Additional marker customization passed to Plotly trace markers.

    Returns
    -------
    go.Figure
        Plotly figure object containing the frequency plot.

    Raises
    ------
    ValueError
        If `x` or `covariate` columns are not in the DataFrame.
    ValueError
        If `x` or `covariate` is a datetime column.
    ValueError
        If the covariate has more than 20 unique categories.
    UserWarning
        If there are NaNs or datetime covariates detected during plotting.

    Examples
    --------
    >>> df = pd.DataFrame({
    >>>         'x1':np.random.random(100),
    >>>         'x2':np.random.choice(['a', 'b', 'c'], 100),
    >>>         'x3':np.random.choice([1, 2, 3], 100),
    >>>     })

    >>> fig = frequency(df, x="x1", show_rug=True)
    >>> fig.show()

    >>> fig = frequency(df, x="x1", covariate="x2", colors=["black"])
    >>> fig.show()

    >>> fig = frequency(df, x="x3", sort_x=False, opacity=0.6, categorical=True)
    >>> fig.show()
    """

    if (df is None) and isinstance(x, (list, np.ndarray)):
        if (covariate is not None) and isinstance(covariate, (list, np.ndarray)):
            df = pd.DataFrame(data={'x': x, 'covariate': covariate})
            x = 'x'
            covariate = 'covariate'
        else:
            df = pd.DataFrame(data={'x': x})
            x = 'x'
    elif (df is None) and isinstance(x, str):
        raise ValueError("DataFrame cannot be None")
    df = df.copy()

    if (df is not None) and (not isinstance(x, str)):
        raise ValueError(f'Since `df` is specified, x and covariate need to be strings columns')
    if x not in df.columns:
        raise ValueError(f"Column '{x}' not found in DataFrame")
    
    if covariate == x:
        covariate = None
    if (covariate is not None):
        if (covariate not in df.columns):
            raise ValueError(f"Covariate '{covariate}' not found in DataFrame")
        if pd.api.types.is_datetime64_any_dtype(df[covariate]):
            warnings.warn(f'Column "{covariate}" is datetime64, so frequency is not suitable', category=UserWarning)
            covariate = None
        if len(df[covariate].unique()) > 20:
            raise ValueError(f"There are more than 20 categories in {covariate}, therefore visuals won't be useful")
    
    if pd.api.types.is_datetime64_any_dtype(df[x]):
        raise ValueError(f'Column "{x}" is datetime64, so frequency is not suitable')

    if categorical is None:
        categorical = pd.api.types.is_object_dtype(df[x]) or \
                    isinstance(df[x], pd.CategoricalDtype)
    if categorical:
        df[x] = df[x].fillna('NaN')
    else:
        df[x] = df[x].replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=x)

    if (bin_size is None) and (not categorical):
        range_ = df[x].max() - df[x].min()
        bin_size = range_/15

    if categorical:
        try:
            sorted_categories = sorted(df[x].dropna().unique().tolist())
            df[x] = pd.Categorical(df[x], categories=sorted_categories, ordered=True)
            df = df.sort_values(by=x)
        except Exception as e:
            ...
            
        # This is used in case of categorical with covariates
        if (covariate is not None):
            grouped = df.groupby([x, covariate], observed=False).size().reset_index(name='count')
            fig = go.Figure()

            for i, group in enumerate(grouped[covariate].unique()):
                sub_data = grouped[grouped[covariate] == group]
                fig.add_trace(go.Bar(
                    x=sub_data[x], y=sub_data['count'],
                    name=str(group), marker_color=colors[i] if colors and i < len(colors) else None,
                    marker=marker_kwargs, **(bar_kwargs or {})
                ))
                
        # This is used in case of categorical without covariates
        else:
            counts = df[x].value_counts().reset_index()
            if sort_x:
                counts = counts.sort_values(by=f'{x}')
            counts.columns = [x, 'count']
            fig = go.Figure(data=[go.Bar(
                x=counts[x], y=counts['count'],
                name='freq',
                marker_color=colors[0] if colors else 'rgba(0, 0, 0, 0.9)',
                marker=marker_kwargs, **(bar_kwargs or {})
            )])
            fig.update_layout(showlegend=False)

        plotlymodex.main_layout(fig, y='frequency', x=f'{x}', title=f'Frequency of {x}', barcornerradius=10, **(layout_kwargs or {}))

        for trace in fig.data:
            trace.marker.opacity = opacity

        return fig

    else:
        # This is used in case of continuous with covariates
        if (covariate is not None):
            group_labels = df[f'{covariate}'].unique().tolist()
            grouped_data = [df[df[f'{covariate}'] == cov][f'{x}'] for cov in group_labels]
            if min_max:
                for idx in range(len(grouped_data)):
                    grouped_data[idx] = pd.concat([grouped_data[idx], pd.Series([df[f'{x}'].min(), df[f'{x}'].max()])])
        # This is used in case of continuous without covariates
        else:
            group_labels = [x]
            grouped_data = [df[f'{x}']]
        drop = []
        for i, label_ in enumerate(group_labels):
            if pd.isna(label_):  # catches both None and NaN
                drop.append(i)
                warnings.warn('Attention: there are NaN values and they will not be considered in the analysis\nIt might be present in some category!')
        # Remove from the list by index (in reverse order to avoid shifting)
        for i in reversed(drop):
            del group_labels[i]
            del grouped_data[i]

        if isinstance(colors, str):
            colors = [colors]
        if covariate is not None and isinstance(colors, list):
            if (len(colors) < len(covariate)):
                colors = colors + px.colors.qualitative.D3[:len(group_labels)]

        fig = ff.create_distplot(
            hist_data=grouped_data, group_labels=group_labels, bin_size=bin_size, 
            colors=colors, histnorm=histnorm,
            show_curve=show_curve, show_hist=show_hist, show_rug=show_rug
        )

        plotlymodex.main_layout(fig, y='frequency', x=f'{x}', title=f'Frequency of {x}', **(layout_kwargs or {}))

        for trace in fig.data:
            trace.marker.opacity = opacity

        # This is used in case of continuous without covariates
        if covariate is None:
            fig.layout.showlegend = False
            for trace in fig.data:
                if colors is None:
                    trace.marker.color = 'black'

        return fig