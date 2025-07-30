import numpy as np
import pandas as pd
from typing import Any, Callable, Sequence
from virtualitics_sdk.assets.dataset import Dataset as Dataset
from virtualitics_sdk.elements import plot as plot
from virtualitics_sdk.elements.element import Element as Element
from virtualitics_sdk.elements.line import HorizontalLine as HorizontalLine, LineType as LineType, OLSTrendLine as OLSTrendLine, VerticalLine as VerticalLine

def get_axis_domain(axis_key: str, data_keys: dict[str, plot.PlotDataKey], bounds: dict[str, list[str | int]] | None): ...
def get_bounds(bounds: dict[str, list[str | int]] | None, key: str, _data_frame: pd.DataFrame, y_axis_key: str, data_type: plot.PlotDataType, y_axis_scale: plot.PlotAxisScale, plot_type: plot.PlotType): ...
def create_bar_plot(data_frame: Dataset | pd.DataFrame, x_axis_key: str, y_axis_key: str, plot_title: str, plot_description: str = '', show_tooltip: bool = True, include_keys_tooltip: list[str] | None = None, exclude_keys_tooltip: list[str] | None = None, x_axis_orientation: plot.XAxisOrientation = ..., y_axis_orientation: plot.YAxisOrientation = ..., x_axis_scale: plot.PlotAxisScale = ..., y_axis_scale: plot.PlotAxisScale = ..., x_axis_label: str | None = None, y_axis_label: str | None = None, color_by: str | None = None, bounds: dict[str, list[str | int]] | None = None, color_by_category: bool = True, show_title: bool = True, show_description: bool = True, colors: list[str] | None = None, advanced_tooltip: Callable[[dict], list[Element | str]] | None = None, legend: list[str] | None = None, lines: list[dict[str, LineType | str | Any]] | None = None, **kwargs) -> plot.Plot:
    '''Generates a Bar Plot for using Virtualitics AI Platform\'s Visualization Framework.
    
    :param data_frame: The data that should be plotted. NOTE: Rows with NaN will be filtered out.
    :param x_axis_key: The name of the column for the X-Axis.
    :param y_axis_key: The name of the column for the Y-Axis.
    :param plot_title: The title of the plot.
    :param plot_description: The description of the plot, defaults to "".
    :param show_tooltip: whether to show the tooltip, defaults to True.
    :param include_keys_tooltip: Keys to include on tooltip, defaults to all keys.
    :param exclude_keys_tooltip: Keys to exclude on tooltip, defaults to including all keys.
    :param x_axis_orientation: The orientation of the X-Axis, defaults to XAxisOrientation.BOTTOM.
    :param y_axis_orientation: The orientation of the Y-Axis, defaults to YAxisOrientation.LEFT.
    :param x_axis_scale: The scale of the X-Axis, defaults to PlotAxisScale.AUTO.
    :param y_axis_scale: The scale of the Y-Axis, defaults to PlotAxisScale.LINEAR.
    :param x_axis_label: The label for the X-axis, defaults to x_axis_key.
    :param y_axis_label: The label for the Y-axis, defaults to y_axis_key.
    :param color_by: The column to use to color the plot if coloring, defaults to None (no coloring).
    :param bounds: The bounds of the data range if they should be manually set. This is a dict that contains they key as a string and a
                   list of two numbers as min and max range. A list of strings is also accepted for categorical values, defaults to None.
                   For example {x_axis_key: [0, 100], y_axis_key: [50, 200]}
    :param color_by_category: When true, the color by axis will be categorical (if set).
    :param show_title:
    :param show_description:
    :param colors: The hex color schema a plot should use, defaults to None (Virtualitics AI Platform default colors).
    :param advanced_tooltip: The function to call that creates an advanced tooltip. This functions takes
                             a dict containing the data point and returns a list of elements (Plots, Infographics
                             Tables, Infographics, CustomEvents) or strings which are rendered as markdown, defaults to None
    :param legend: A list to represent the order and labels on the legend. Will default to order present in plot data.
    :param lines: A list of dictionaries containing information on parameters for the creation of a line on the plot.
                  Each dictionary in the list denotes a different line. The currently supported line types are
                  \'horizontal\', \'vertical\', and \'linear\', where a \'linear\' line denotes a linear trend line fitted to
                  the data. The dictionary must be specify the line type using a `LineType` enum and can specify
                  additional parameters relevant each line type. See the constructors for the HorizontalLine,
                  VerticalLine, and OLSTrendLine for more information. For exmaple, a dictionary for a linear trend line
                  could look like: {"type": LineType.LINEAR, "description": "My trendline",
                  "time_series_unit": pd.Timedelta("1 hours")}.
    :return: A newly created bar plot.

    **EXAMPLE:** 
       
       .. code-block:: python

           # Imports 
           from virtualitics_sdk import create_bar_plot
           ...
           # Example usage
           df = pd.read_csv("some/example/path.csv")
           ex_bar = create_bar_plot(df, 
                                    "sepal.length", 
                                    "sepal.width", 
                                    "Sepal Length vs. Sepal Width")
           card = Card("Example", [ex_bar])
    '''
def create_histogram_plot(data_frame: Dataset | pd.DataFrame, data_column: str, plot_title: str, plot_description: str = '', bins: int | Sequence[int | float | np.number] | str = 'auto', frequency: bool = False, show_tooltip: bool = True, include_keys_tooltip: list[str] | None = None, exclude_keys_tooltip: list[str] | None = None, x_axis_orientation: plot.XAxisOrientation = ..., y_axis_orientation: plot.YAxisOrientation = ..., x_axis_scale: plot.PlotAxisScale = ..., y_axis_scale: plot.PlotAxisScale = ..., x_axis_label: str | None = None, y_axis_label: str | None = None, color_by: str | None = None, bounds: dict[str, list[str | int]] | None = None, color_by_category: bool = True, show_title: bool = True, show_description: bool = True, _id: str | None = None, colors: list[str] | None = None, advanced_tooltip: Callable[[dict], list[Element | str]] | None = None, lines: list[dict[str, LineType | str | Any]] | None = None, legend: list[str] | None = None, **kwargs) -> plot.Plot:
    '''Generates a Histogram Plot using Virtualitics AI Platform\'s Visualization Framework.
    
    :param data_frame: The data that should be plotted. NOTE: Rows with NaN will be filtered out.
    :param data_column: The name of the column whose data will be plotted in the histogram.
    :param plot_title: The title of the plot.
    :param plot_description: The description of the plot, defaults to "".
    :param bins: If an integer is provided, this is number of bins to to plot in the histogram. If a sequence of numbers is provided,
                 these denote the edges of the bins, including the right most edge. If a string is provided, a binning algorithm is
                 used to determine the number of bins based on the data\'s distribution. More details can be found
                 `here <https://numpy.org/doc/stable/reference/generated/numpy.histogram_bin_edges.html#numpy.histogram_bin_edges>`_,
                 defaults to \'auto\'.
    :param frequency: Determines whether to plot a histogram based on counts or frequency. If False, the histogram is plotted using
                      counts in each bin. If True, uses frequency instead, defaults to False.
    :param show_tooltip: whether to show the tooltip, defaults to True.
    :param include_keys_tooltip: Keys to include on tooltip, defaults to all keys.
    :param exclude_keys_tooltip: Keys to exclude on tooltip, defaults to including all keys.
    :param x_axis_orientation: The orientation of the X-Axis, defaults to XAxisOrientation.BOTTOM.
    :param y_axis_orientation: The orientation of the Y-Axis, defaults to YAxisOrientation.LEFT.
    :param x_axis_scale: The scale of the X-Axis, defaults to PlotAxisScale.AUTO.
    :param y_axis_scale: The scale of the Y-Axis, defaults to PlotAxisScale.LINEAR.
    :param x_axis_label: The label for the X-axis, defaults to x_axis_key.
    :param y_axis_label: The label for the Y-axis, defaults to y_axis_key.
    :param color_by: The column to use to color the plot if coloring, defaults to None (no coloring).
    :param bounds: The bounds of the data range if they should be manually set. This is a dict that contains they key as a string and a
                   list of two numbers as min and max range. A list of strings is also accepted for categorical values, defaults to None.
                   For example {x_axis_key: [0, 100], y_axis_key: [50, 200]}
    :param color_by_category: When true, the color by axis will be categorical (if set).
    :param show_title:
    :param show_description:
    :param _id: The ID of the plot, defaults to None.
    :param colors: The hex color schema a plot should use, defaults to None (Virtualitics AI Platform default colors).
    :param advanced_tooltip: The function to call that creatse an advanced tooltip. This functions takes
                             a dict containing the data point and returns a list of elements (Plots, Infographics
                             Tables, Infographics, CustomEvents) or strings which are rendered as markdown, defaults to None
    :param lines: A list of dictionaries containing information on parameters for the creation of a line on the plot.
                  Each dictionary in the list denotes a different line. The currently supported line types are
                  \'horizontal\', \'vertical\', and \'linear\', where a \'linear\' line denotes a linear trend line fitted to
                  the data. The dictionary must be specify the line type using a `LineType` enum and can specify
                  additional parameters relevant each line type. See the constructors for the HorizontalLine,
                  VerticalLine, and OLSTrendLine for more information. For exmaple, a dictionary for a linear trend line
                  could look like: {"type": LineType.LINEAR, "description": "My trendline",
                  "time_series_unit": pd.Timedelta("1 hours")}.
    :param legend: A list to represent the order and labels on the legend. Will default to order present in plot data.
    :return: A newly created bar plot.

    **EXAMPLE:** 
       
       .. code-block:: python
       
           # Imports 
           from virtualitics_sdk import create_histogram_plot
           . . . 
           # Example usage 
           df = pd.read_csv("some/example/path.csv")
           ex_histogram_plot = create_histogram_plot(df, 
                                                     "sepal.length", 
                                                     "Sepal Length Distribution",
                                                     advanced_tooltip=bar_tooltip)
           card = Card("Example",[ex_histogram_plot])
    '''
def create_scatter_plot(data_frame: Dataset | pd.DataFrame, x_axis_key: str, y_axis_key: str, plot_title: str, plot_description: str = '', show_tooltip: bool = True, include_keys_tooltip: list[str] | None = None, exclude_keys_tooltip: list[str] | None = None, x_axis_orientation: plot.XAxisOrientation = ..., y_axis_orientation: plot.YAxisOrientation = ..., x_axis_scale: plot.PlotAxisScale = ..., y_axis_scale: plot.PlotAxisScale = ..., x_axis_label: str | None = None, y_axis_label: str | None = None, color_by: str | None = None, bounds: dict[str, list[str | int]] | None = None, color_by_category: bool = True, show_title: bool = True, show_description: bool = True, colors: list[str] | None = None, advanced_tooltip: Callable[[dict], list[Element | str]] | None = None, lines: list[dict[str, LineType | str | Any]] | None = None, legend: list[str] | None = None, **kwargs) -> plot.Plot:
    '''Generates a Scatter Plot for using Virtualitics AI Platform\'s Visualization Framework.
    
    :param data_frame: The data that should be plotted. NOTE: Rows with NaN will be filtered out.
    :param x_axis_key: The name of the column for the X-Axis.
    :param y_axis_key: The name of the column for the Y-Axis.
    :param plot_title: The title of the plot.
    :param plot_description: The description of the plot, defaults to "".
    :param show_tooltip: whether to show the tooltip, defaults to True.
    :param include_keys_tooltip: Keys to include on tooltip, defaults to all keys.
    :param exclude_keys_tooltip: Keys to exclude on tooltip, defaults to including all keys.
    :param x_axis_orientation: The orientation of the X-Axis, defaults to XAxisOrientation.BOTTOM.
    :param y_axis_orientation: The orientation of the Y-Axis, defaults to YAxisOrientation.LEFT.
    :param x_axis_scale: The scale of the X-Axis, defaults to PlotAxisScale.AUTO.
    :param y_axis_scale: The scale of the Y-Axis, defaults to PlotAxisScale.LINEAR.
    :param x_axis_label: The label for the X-axis, defaults to x_axis_key.
    :param y_axis_label: The label for the Y-axis, defaults to y_axis_key.
    :param color_by: The column to use to color the plot if coloring, defaults to None (no coloring).
    :param bounds: The bounds of the data range if they should be manually set. This is a dict that contains they key as a string and a
                   list of two numbers as min and max range. A list of strings is also accepted for categorical values, defaults to None.
                   For example {x_axis_key: [0, 100], y_axis_key: [50, 200]}
    :param color_by_category: When true, the color by axis will be categorical (if set).
    :param show_title:
    :param show_description:
    :param colors: The hex color schema a plot should use, defaults to None (Virtualitics AI Platform default colors).
    :param advanced_tooltip: The function to call that creatse an advanced tooltip. This functions takes
                             a dict containing the data point and returns a list of elements (Plots, Infographics
                             Tables, Infographics, CustomEvents) or strings which are rendered as markdown, defaults to None
    :param lines: A list of dictionaries containing information on parameters for the creation of a line on the plot.
                  Each dictionary in the list denotes a different line. The currently supported line types are
                  \'horizontal\', \'vertical\', and \'linear\', where a \'linear\' line denotes a linear trend line fitted to
                  the data. The dictionary must be specify the line type using a `LineType` enum and can specify
                  additional parameters relevant each line type. See the constructors for the HorizontalLine,
                  VerticalLine, and OLSTrendLine for more information. For exmaple, a dictionary for a linear trend line
                  could look like: {"type": LineType.LINEAR, "description": "My trendline",
                  "time_series_unit": pd.Timedelta("1 hours")}.
    :param legend: A list to represent the order and labels on the legend. Will default to order present in plot data.
    :return: A newly created scatter plot.

    **EXAMPLE:** 
       
       .. code-block:: python
       
           # Imports 
           from virtualitics_sdk import create_scatter_plot
           . . . 
           df = pd.read_csv("some/example/path.csv")
           ex_scatter_plot = create_scatter_plot(df, 
                                                 "sepal.length", 
                                                 "sepal.width", 
                                                 "Sepal Length vs. Sepal Width")
           card = Card("",[ex_scatter_plot])
                        
    The above plot will be displayed as:   

       .. image:: ../images/scatter_ex.png
          :align: center
    '''
def create_line_plot(data_frame: Dataset | pd.DataFrame, x_axis_key: str, y_axis_key: str, plot_title: str, plot_description: str = '', show_tooltip: bool = True, include_keys_tooltip: list[str] | None = None, exclude_keys_tooltip: list[str] | None = None, x_axis_orientation: plot.XAxisOrientation = ..., y_axis_orientation: plot.YAxisOrientation = ..., x_axis_scale: plot.PlotAxisScale = ..., y_axis_scale: plot.PlotAxisScale = ..., x_axis_label: str | None = None, y_axis_label: str | None = None, color_by: str | None = None, bounds: dict[str, list[str | int]] | None = None, color_by_category: bool = True, show_title: bool = True, show_description: bool = True, colors: list[str] | None = None, advanced_tooltip: Callable[[dict], list[Element | str]] | None = None, lines: list[dict[str, LineType | str | Any]] | None = None, legend: list[str] | None = None, **kwargs) -> plot.Plot:
    '''Generates a Line Plot for using Virtualitics AI Platform\'s Visualization Framework.
    
    :param data_frame: The data that should be plotted. NOTE: Rows with NaN will be filtered out.
    :param x_axis_key: The name of the column for the X-Axis.
    :param y_axis_key: The name of the column for the Y-Axis.
    :param plot_title: The title of the plot.
    :param plot_description: The description of the plot, defaults to "".
    :param show_tooltip: whether to show the tooltip, defaults to True.
    :param include_keys_tooltip: Keys to include on tooltip, defaults to all keys.
    :param exclude_keys_tooltip: Keys to exclude on tooltip, defaults to including all keys.
    :param x_axis_orientation: The orientation of the X-Axis, defaults to XAxisOrientation.BOTTOM.
    :param y_axis_orientation: The orientation of the Y-Axis, defaults to YAxisOrientation.LEFT.
    :param x_axis_scale: The scale of the X-Axis, defaults to PlotAxisScale.AUTO.
    :param y_axis_scale: The scale of the Y-Axis, defaults to PlotAxisScale.LINEAR.
    :param x_axis_label: The label for the X-axis, defaults to x_axis_key.
    :param y_axis_label: The label for the Y-axis, defaults to y_axis_key.
    :param color_by: The column to use to color the plot if coloring, defaults to None (no coloring).
    :param bounds: The bounds of the data range if they should be manually set. This is a dict that contains the key as a string and a
                   list of two numbers as min and max range. A list of strings is also accepted for categorical values, defaults to None.
                   For example {x_axis_key: [0, 100], y_axis_key: [50, 200]}
    :param color_by_category: When true, the color by axis will be categorical (if set).
    :param show_title:
    :param show_description:
    :param colors: The hex color schema a plot should use, defaults to None (Virtualitics AI Platform default colors).
    :param advanced_tooltip: The function to call that creatse an advanced tooltip. This functions takes
                             a dict containing the data point and returns a list of elements (Plots, Infographics
                             Tables, Infographics, CustomEvents) or strings which are rendered as markdown, defaults to None
    :param lines: A list of dictionaries containing information on parameters for the creation of a line on the plot.
                  Each dictionary in the list denotes a different line. The currently supported line types are
                  \'horizontal\', \'vertical\', and \'linear\', where a \'linear\' line denotes a linear trend line fitted to
                  the data. The dictionary must be specify the line type using a `LineType` enum and can specify
                  additional parameters relevant each line type. See the constructors for the HorizontalLine,
                  VerticalLine, and OLSTrendLine for more information. For exmaple, a dictionary for a linear trend line
                  could look like: {"type": LineType.LINEAR, "description": "My trendline",
                  "time_series_unit": pd.Timedelta("1 hours")}.
    :param legend: A list to represent the order and labels on the legend. Will default to order present in plot data.
    :return: A newly created line plot.

    **EXAMPLE:** 
       
       .. code-block:: python
       
           # Imports 
           from virtualitics_sdk import create_line_plot
           . . . 
           df = pd.read_csv("some/example/path.csv")
           ex_line_plot = create_line_plot(df, 
                                           "sepal.length", 
                                           "sepal.width", 
                                           "Sepal Length vs. Sepal Width Line")
           card = Card("",[ex_line_plot])

    The above plot will be displayed as:   

       .. image:: ../images/line_ex.png
          :align: center
    '''
def create_plot(plot_type: plot.PlotType, data_frame: Dataset | pd.DataFrame, x_axis_key: str, y_axis_key: str, plot_title: str, plot_description: str = '', show_tooltip: bool = True, include_keys_tooltip: list[str] | None = None, exclude_keys_tooltip: list[str] | None = None, x_axis_orientation: plot.XAxisOrientation = ..., y_axis_orientation: plot.YAxisOrientation = ..., x_axis_scale: plot.PlotAxisScale = ..., y_axis_scale: plot.PlotAxisScale = ..., x_axis_label: str | None = None, y_axis_label: str | None = None, color_by: str | None = None, bounds: dict[str, list[str | int]] | None = None, color_by_category: bool = True, show_title: bool = True, show_description: bool = True, colors: list[str] | None = None, advanced_tooltip: Callable[[dict], list[Element | str]] | None = None, lines: list[dict[str, LineType | str | Any]] | None = None, legend: list[str] | None = None, **kwargs) -> plot.Plot:
    '''Generates a Plot for using Virtualitics AI Platforms\'s Visualization Framework.

    :param plot_type:
    :param data_frame: The data that should be plotted. NOTE: Rows with NaN will be filtered out.
    :param x_axis_key: The name of the column for the X-Axis.
    :param y_axis_key: The name of the column for the Y-Axis.
    :param plot_title: The title of the plot.
    :param plot_description: The description of the plot, defaults to "".
    :param show_tooltip: whether to show the tooltip, defaults to True.
    :param include_keys_tooltip: Keys to include on tooltip, defaults to all keys.
    :param exclude_keys_tooltip: Keys to exclude on tooltip, defaults to including all keys.
    :param x_axis_orientation: The orientation of the X-Axis, defaults to XAxisOrientation.BOTTOM.
    :param y_axis_orientation: The orientation of the Y-Axis, defaults to YAxisOrientation.LEFT.
    :param x_axis_scale: The scale of the X-Axis, defaults to PlotAxisScale.LINEAR.
    :param y_axis_scale: The scale of the Y-Axis, defaults to PlotAxisScale.LINEAR.
    :param x_axis_label: The label for the X-axis, defaults to the x_axis_key.
    :param y_axis_label: The label for the Y-axis, defaults to the y_axis_key.
    :param color_by: The column to use to color the plot if coloring. Defaults to None (no coloring).
    :param bounds: The bounds of the data range if they should be manually set. This is a dict that
                   contains they key as a string and a list of two numbers as min and max range. A list
                   of strings is also accepted for categorical values. For example {x_axis_key: [0, 100], y_axis_key: [50, 200]}
    :param color_by_category: When true, the color by axis will be categorical (if set).
    :param show_title:
    :param show_description:
    :param colors: The hex color schema a plot should use, defaults to None (Virtualitics AI Platform default colors).
    :param advanced_tooltip: The function to call that creatse an advanced tooltip. This functions takes
                             a dict containing the data point and returns a list of elements (Plots, Infographics
                             Tables, Infographics, CustomEvents) or strings which are rendered as markdown, defaults to None
    :param lines: A list of dictionaries containing information on parameters for the creation of a line on the plot.
                  Each dictionary in the list denotes a different line. The currently supported line types are
                  \'horizontal\', \'vertical\', and \'linear\', where a \'linear\' line denotes a linear trend line fitted to
                  the data. The dictionary must be specify the line type using a `LineType` enum and can specify
                  additional parameters relevant each line type. See the constructors for the HorizontalLine,
                  VerticalLine, and OLSTrendLine for more information. For exmaple, a dictionary for a linear trend line
                  could look like: {"type": LineType.LINEAR, "description": "My trendline",
                  "time_series_unit": pd.Timedelta("1 hours")}.
    :param legend: A list to represent the order and labels on the legend. Will default to order present in plot data.
    :return: A Plot with the specification from above.
    '''
