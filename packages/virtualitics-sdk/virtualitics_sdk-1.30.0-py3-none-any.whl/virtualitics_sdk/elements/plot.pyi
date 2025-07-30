import pandas
from _typeshed import Incomplete
from datetime import datetime as datetime
from enum import Enum
from predict_backend.validation.type_validation import validate_types
from typing import Callable
from virtualitics_sdk.elements.element import Element as Element, ElementType as ElementType
from virtualitics_sdk.elements.line import Line as Line

logger: Incomplete
PLOT_SIZE_THRESHOLD: int

class TooltipStatus(Enum):
    PENDING: str
    SUCCESS: str
    ERROR: str

class PlotType(Enum):
    SCATTER: str
    BAR: str
    LINE: str
    WATERFALL: str
    PLOTLY: str

PLOT_TYPES: Incomplete
ALLOWED_TOOLTIP_TYPES: Incomplete

class XAxisOrientation(Enum):
    TOP: str
    BOTTOM: str

class YAxisOrientation(Enum):
    LEFT: str
    RIGHT: str

class PlotAxisType(Enum):
    NUMBER: str
    CATEGORY: str

class PlotAxisScale(Enum):
    AUTO: str
    LINEAR: str
    POW: str
    SQUARE_ROOT: str
    LOGARITHMIC: str
    IDENTITY: str
    TIME: str
    BAND: str
    POINT: str
    ORDINAL: str
    QUANTILE: str
    QUANTIZE: str
    UTC: str
    SEQUENTIAL: str
    THRESHOLD: str

class PlotDataType(Enum):
    CATEGORY: str
    DATE: str
    NUMBER: str

class PlotDataKey:
    type: Incomplete
    domain: Incomplete
    tooltip: Incomplete
    color: Incomplete
    legend: Incomplete
    @validate_types
    def __init__(self, _type: PlotDataType, domain: list[int] | list[float] | list[str] | list[datetime] | list[pandas.Timestamp], tooltip: bool, color: list[str] | None = None, legend: list[str] | None = None) -> None:
        """Information about plotting a specific data key.

        :param _type: The type of plot data (category, date or number).
        :param domain: The min and max of the data if a date or number type. If category this is a list of all possible values.
        :param tooltip: whether this key should be included in the tooltip.

        :raises ValueError: If domain is invalid.
        """
    def to_json(self): ...

class XAxis:
    orientation: Incomplete
    scale: Incomplete
    label: Incomplete
    data_key: Incomplete
    domain: Incomplete
    @validate_types
    def __init__(self, orientation: XAxisOrientation, scale: PlotAxisScale, label: str, data_key: str, domain: list[int | float | str] | None = None) -> None: ...
    def to_json(self): ...

class YAxis:
    orientation: Incomplete
    scale: Incomplete
    label: Incomplete
    data_key: Incomplete
    domain: Incomplete
    @validate_types
    def __init__(self, orientation: YAxisOrientation, scale: PlotAxisScale, label: str, data_key: str, domain: list[int | float | str] | None = None) -> None: ...
    def to_json(self): ...

class PlotDataPoint:
    id: Incomplete
    extra_keys: Incomplete
    def __init__(self, _id: int, **kwargs) -> None:
        """A Data Point to be shown on a plot.

        :param _id: The ID for this data point.
        :param kwargs: Data values (i.e. {'colA': 2, 'colB': -1.3).
        """
    def to_json(self): ...

class Plot(Element):
    '''
    A VAIP Plot instance.

    To see usage of the Plot class look to :class:`~virtualitics_sdk.utils.viz_utils` where plots
    are generated with utility functions.

    :param title: The title of the blot.
    :param _type: The type of plot (can be "scatter", "bar", or "line").
    :param x_axis: The X-Axis.
    :param y_axis: The Y-Axis.
    :param data: The data points needed for the plot.
    :param has_tooltip: Whether this plot should show a tooltip.
    :param data_keys: The keys within data point that should be rendered as the values.
    :param description: The description of this plot, defaults to \'\'.
    :param color_by: The column to use to color the plot if coloring, defaults to None (no coloring).
    :param show_title: Whether to show the title on the page when rendered, defaults to True.
    :param show_description: Whether to show the description to the page when rendered, defaults to True.
    :param colors: The colors schema a plot should use, defaults to None (Predict default colors).
    :param advanced_tooltip: The function to call that create an advanced tooltip. This functions takes
                                a dict containing the data point and returns a list of elements (Plots, Infographics
                                Tables, Infographics, CustomEvents) or strings which are rendered as markdown, defaults
                                to None
    :param lines: A list of `Line` objects that will be displayed in the plot. See documentation for each type of
                    `Line` class for more information, defaults to None.
    :param legend: The explicit order for the legend of a categorical plot. If not set, the legend will be
                automatically determined from the plot\'s data

    '''
    title: Incomplete
    plot_type: Incomplete
    description: Incomplete
    x_axis: Incomplete
    y_axis: Incomplete
    persistence: Incomplete
    plot_empty: Incomplete
    has_tooltip: Incomplete
    data_keys: Incomplete
    color_by: Incomplete
    colors: Incomplete
    has_advanced_tooltip: bool
    legend: Incomplete
    tooltip_func: Incomplete
    tooltip_func_name: Incomplete
    tooltip_status: Incomplete
    lines: Incomplete
    additional_args: Incomplete
    @validate_types
    def __init__(self, title: str, _type: PlotType, x_axis: XAxis, y_axis: YAxis, data: list[PlotDataPoint], has_tooltip: bool, data_keys: dict[str, PlotDataKey], description: str = '', color_by: str | None = None, show_title: bool = True, show_description: bool = True, colors: list[str] | None = None, advanced_tooltip: Callable[[dict], list[Element | str]] | None = None, lines: list[Line] = [], legend: list[str] | None = None, **kwargs) -> None: ...
    def to_json(self): ...
    @staticmethod
    def is_valid_plot_type(s: str) -> bool: ...
