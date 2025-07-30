import os
import sys
import copy

import plotly.subplots as subplots

sys.path.append(os.path.abspath('..'))
from graphmodex import plotlymodex


__all__ = [
    'subplot'
]


def subplot(figs:list, rows:int=1, cols:int=2, subplot_titles:list[str]=None, title:str='Plots',
            width:int=1400, height:int=600, legends:list[bool]=[],
            shared_xaxes:bool=False, shared_yaxes:bool=False,
            horizontal_spacing:float=0.08, vertical_spacing:float=0.08,
            layout_kwargs:dict=None, subplots_kwargs:dict=None):
    """
    Combine multiple Plotly figures into a single subplot layout with shared configuration.

    Parameters
    ----------
    figs : list of go.Figure
        List of Plotly figures to combine into subplots.
    rows : int, optional
        Initial number of rows in the subplot grid. Adjusted automatically if not sufficient.
        Default is 1.
    cols : int, optional
        Number of columns in the subplot grid. Default is 2.
    subplot_titles : list of str, optional
        Titles for each subplot. If None, titles are taken from the individual figures' titles.
    title : str, optional
        Title for the entire figure. Default is 'Plots'.
    width : int, optional
        Width of the entire figure in pixels. Default is 1400.
    height : int, optional
        Height of the entire figure in pixels. Default is 600. Increased if more rows are added.
    legends : list of bool, optional
        List specifying whether to show legend for each subplot. Defaults to showing all.
    shared_xaxes : bool, optional
        Whether x-axes should be shared across subplots. Default is False.
    shared_yaxes : bool, optional
        Whether y-axes should be shared across subplots. Default is False.
    horizontal_spacing : float, optional
        Spacing between subplot columns as a fraction of the plot width. Default is 0.08.
    vertical_spacing : float, optional
        Spacing between subplot rows as a fraction of the plot height. Default is 0.08.
    layout_kwargs : dict, optional
        Additional layout settings to apply to the main figure. (Unused in current version)
    subplots_kwargs : dict, optional
        Additional keyword arguments passed to `make_subplots`.

    Returns
    -------
    go.Figure
        A combined Plotly figure with subplots arranged in the specified layout.

    Raises
    ------
    ValueError
        If the input `figs` list is empty.

    Examples
    --------
    >>> from graphmodex import plotlymodex
    >>> 
    >>> fig1 = go.Figure()
    >>> fig1.add_trace(go.Scatter(x=x1, y=y1))
    >>> fig2 = go.Figure()
    >>> fig1.add_trace(go.Scatter(x=x2, y=y2))
    >>> 
    >>> plotlymodex.subplot(
    >>>         figs=[fig1, fig2], rows=1, cols=2,
    >>>         subplot_titles=['Fig 1', 'Fig 2'],
    >>>         width=700, height=700
    >>>     )
    >>> fig.show()
    >>> 
    >>> plotlymodex.subplot(
    >>>         figs=[fig1, fig2], rows=2, cols=1,
    >>>         subplot_titles=['Fig 1', 'Fig 2'],
    >>>         title='Plots', legends=[1, 0]
    >>>     )
    >>> fig.show()
    """
    if len(figs) == 0:
        raise ValueError("The 'figs' argument must contain at least one figure.")
    
    figs = [copy.deepcopy(f) for f in figs]

    while len(legends) < len(figs):
        legends.append(1)
    legends = [bool(x) for x in legends]
    for i, fig_ in enumerate(figs):
        for trace_ in fig_.data:
            trace_.showlegend = legends[i]

    while rows*cols < len(figs):
        rows += 1
        height += 400
        vertical_spacing = 0.1
    
    if subplot_titles is None:
        subplot_titles = []
        for fig_ in figs:
            subplot_titles.append(fig_.layout['title']['text'])

    fig = subplots.make_subplots(
        rows=rows, cols=cols, subplot_titles=subplot_titles,
        shared_xaxes=shared_xaxes, shared_yaxes=shared_yaxes, 
        horizontal_spacing=horizontal_spacing, vertical_spacing=vertical_spacing,
        **(subplots_kwargs or {})
    )

    for i, f in enumerate(figs):
        row = i // cols + 1
        col = i % cols + 1
        for trace in f.data:
            fig.add_trace(trace, row=row, col=col)

    plotlymodex.main_layout(fig, title=title, width=width, height=height, x='x', y='y')

    return fig