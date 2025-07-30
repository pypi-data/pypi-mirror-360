from typing import Union, Literal
import plotly.graph_objects as go


__all__ = [
    'main_layout',
]


def main_layout(fig:go.Figure, width=700, height=600, title=None, paper_color='white',
                        x='x', y='y', rows=1, cols=2, x_range=None, y_range=None,
                        x_type:Literal["linear","log","date","category","multicategory"]="-",
                        y_type:Literal["linear","log","date","category","multicategory"]="-",
                        x_hover='x', y_hover='y', customdata:Union[str, None]=None, hover_customdata='Info', 
                        legend_border_color:str='#ffffff', legend_background_color:str='#ffffff', legend_border_width:str=1,
                        legend_orientation:Literal['v','h']='v', legend_x:float=None, legend_y:str=None,
                        **kwargs) -> go.Figure:
    """
    Apply a consistent layout and styling configuration to a Plotly figure.

    Parameters
    ----------
    fig : go.Figure
        The Plotly figure to update.
    width : int, optional
        Width of the figure in pixels. Default is 700.
    height : int, optional
        Height of the figure in pixels. Default is 600.
    title : str, optional
        Title of the figure.
    paper_color : str, optional
        Background color for both paper and plot. Default is 'white'.
    x : str, optional
        Label for the x-axis. Default is 'x'.
    y : str, optional
        Label for the y-axis. Default is 'y'.
    rows : int, optional
        Number of subplot rows (unused in this function). Default is 1.
    cols : int, optional
        Number of subplot columns (unused in this function). Default is 2.
    x_range : list or tuple, optional
        Range for the x-axis.
    y_range : list or tuple, optional
        Range for the y-axis.
    x_type : {'linear', 'log', 'date', 'category', 'multicategory'}, optional
        Axis type for the x-axis. Default is "-".
    y_type : {'linear', 'log', 'date', 'category', 'multicategory'}, optional
        Axis type for the y-axis. Default is "-".
    x_hover : str, optional
        Label for x-axis hover text. Default is 'x'.
    y_hover : str, optional
        Label for y-axis hover text. Default is 'y'.
    customdata : str or None, optional
        Custom data to use in hover text. If set to 'no', disables customdata.
    hover_customdata : str, optional
        Label for the custom hover data. Default is 'Info'.
    legend_border_color : str, optional
        Color of the legend border. Default is '#ffffff'.
    legend_background_color : str, optional
        Background color of the legend. Default is '#ffffff'.
    legend_border_width : str, optional
        Width of the legend border. Default is 1.
    legend_orientation : {'v', 'h'}, optional
        Orientation of the legend. Default is 'v'.
    legend_x : float, optional
        X-position of the legend.
    legend_y : str, optional
        Y-position of the legend.
    **kwargs : dict
        Additional layout keyword arguments to pass to `fig.update_layout`.

    Returns
    -------
    go.Figure
        The updated Plotly figure with applied layout and styling.

    Examples
    --------
    >>> from graphmodex import plotlymodex
    >>> 
    >>> fig = go.Figure()
    >>> fig.add_trace(go.Scatter(x=x, y=y))
    >>> 
    >>> plotlymodex.main_layout(
    >>>         fig, title='Figure',
    >>>         x='x', y='f(x)'
    >>>     )
    >>> fig.show()
    >>> 
    >>> plotlymodex.main_layout(
    >>>         fig, title='Figure', x='x', y='f(x)', 
    >>>         x_type='log', legend_x=0.55, legend_y=0.04, 
    >>>         legend_border_color='black', y_range=[0, 1.1]
    >>>     )
    >>> fig.show()
    """    
    fig.update_layout({
        'width':width,
        'height':height,
        'plot_bgcolor':paper_color,
        'paper_bgcolor':paper_color,
        'title':title,
        **kwargs
    })
    
    for xaxis in fig.select_xaxes():
        xaxis.update(
            showgrid=True,
            gridcolor='#CCCCCC',
            zerolinecolor='#AAAAAA',
            linecolor='black',
            title=x,
            range=x_range,
            type=x_type,
        )
    for yaxis in fig.select_yaxes():
        yaxis.update(
            showgrid=True,
            gridcolor='#CCCCCC',
            zerolinecolor='#AAAAAA',
            linecolor='black',
            title=y,
            range=y_range,
            type=y_type,
        )
        
    if isinstance(customdata, str) and customdata == 'no':
        ...
    elif customdata is None:
        fig.update_traces(patch={
            'customdata': customdata, 'hovertemplate': x_hover + ': %{x}<br>' + y_hover + ': %{y}'
        })
    else:
        fig.update_traces(patch={
            'customdata': customdata,
            'hovertemplate': x_hover + ': %{x}<br>' + y_hover + ': %{y}<br>' + hover_customdata + ': %{customdata}<br>'
        })

    fig.update_layout(
        showlegend=True,
        legend=dict(
            x=legend_x,
            y=legend_y,
            bgcolor=legend_background_color,
            bordercolor=legend_border_color,
            borderwidth=legend_border_width,
            orientation=legend_orientation,
        )
    )
    
    return fig