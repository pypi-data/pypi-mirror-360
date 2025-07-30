import pandas as pd
from _typeshed import Incomplete
from abc import ABC
from enum import Enum
from predict_backend.validation.type_validation import validate_types

class LineType(Enum):
    HORIZONTAL: str
    VERTICAL: str
    LINEAR: str

class LineDataPoint:
    x: Incomplete
    y: Incomplete
    def __init__(self, x, y) -> None: ...
    def to_json(self): ...

class Line(ABC):
    desc: Incomplete
    def __init__(self, desc: str = '') -> None: ...
    def validate_input(self) -> None: ...
    def to_json(self): ...

class HorizontalLine(Line):
    y: Incomplete
    label: Incomplete
    def __init__(self, label: str, y: Incomplete | None = None, desc: str = '') -> None:
        '''A horizontal line for a plot in predict.

        :param label: A short name to reference the Line in the toggle menu.
        :param y: The y coordinate of the horizontal line. This should be the same data type as what is provided
                  to the plotting function, defaults to None.
        :param desc: A description of the line, defaults to "".
        '''
    def to_json(self): ...

class VerticalLine(Line):
    x: Incomplete
    label: Incomplete
    def __init__(self, label: str, x: Incomplete | None = None, desc: str = '') -> None:
        '''A vertical line for a plot in predict.

        :param label: A short name to reference the Line in the toggle menu.
        :param x: The x coordinate of the vertical line. This should be the same data type as what is provided
                  to the plotting function, defaults to None.
        :param desc: A description of the line, defaults to "".
        '''
    def to_json(self): ...

class OLSTrendLine(Line):
    intersect_origin: Incomplete
    is_time_series: Incomplete
    time_series_scaling_factor: Incomplete
    fit_center: Incomplete
    color_key: Incomplete
    @validate_types
    def __init__(self, data: pd.DataFrame, x_col: str, y_col: str, domain: list[int | float], description: str = '', intersect_origin: bool = False, is_time_series: bool = False, fit_center: bool = True, color_key: str | None = None, time_series_unit=...) -> None:
        '''A linear trend line fitted using Oridinay Least Squares (OLS) regression. This class has additional
        parameters for use with time series data.

        :param data: The dataframe containing the data that will be used to fit the trendline.
        :param x_col: The name of the column in `data` representing the independent variable.
        :param y_col: The name of the column in `data` representing the dependent variable.
        :param domain: A list containing 2 elements of the same data type as the dataframe\'s x column. These values
                       will be used to evaluate the trendline and create endpoints of the trendline.
        :param desc: Description of the trendline, defaults to "".
        :param intersect_origin: Whether to force the trendline to intersect the origin, defaults to False.
        :param is_time_series: Whether the provided x column is a time series, defaults to False.
        :param fit_center: Whether to center the data before fitting a trendline. This can help with numerical
                           stability. This parameter is only relevenat when `is_time_series` is set to False,
                           defaults to True.
        :param color_key: This is useful to link the trendline to a specific line, in the case of a line plot with
                           multiple lines. For example, if you color your line based on the values of a
                           feature, this could be helpful to link the trendline to that line and maybe color it with
                           the same color.
        :param time_series_unit: The unit on which the data will be converted to when calculating trendlines for time
                                 series data. This is only relevant for time series. Defaults to pd.Timedelta("1 days").
        '''
    def to_json(self):
        """
        Converts the trend line object to a JSON serializable dictionary.

        Returns:
            dict: A dictionary representation of the trend line object.
        """
    fit_results: Incomplete
    endpoints: Incomplete
    coefs: Incomplete
    rsquared: Incomplete
    t_values: Incomplete
    std_errors: Incomplete
    def fit_transform(self, data: pd.DataFrame, x_col: str, y_col: str, domain: list): ...
