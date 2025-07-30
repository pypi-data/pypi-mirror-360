from _typeshed import Incomplete
from enum import Enum
from predict_backend.validation.type_validation import validate_types
from virtualitics_sdk.elements.custom_event import CustomEvent as CustomEvent
from virtualitics_sdk.elements.element import Element as Element, ElementType as ElementType
from virtualitics_sdk.exceptions import PredictException as PredictException
from virtualitics_sdk.icons import ALL_ICONS as ALL_ICONS

class InfographicOrientation(Enum):
    ROW: str
    COLUMN: str

class InfographDataType(Enum):
    POSITIVE: str
    NEGATIVE: str
    WARNING: str
    NEUTRAL: str
    INFO: str

class InfographData:
    """The information to show in an infographic block.

    :param label: The label at the top of the infographic block.
    :param main_text: The main bolded text in this infographic block.
    :param supporting_text: The supporting text underneath the main text for the infographic, defaults to ''.
    :param icon: An optional icon to show at the top-right of the infographic. Must be one of the available Google icons which be viewed at :class:`~virtualitics_sdk.icons.fonts`. Defaults to ''.
    :param _type: The type of infographic to show. Sets the themes/colors for this block, defaults to InfographDataType.INFO.
    :param unit: The unit to show alongside the main text, defaults to None.
    :param display_compact: If true, each tile takes up less space than a standard Infograph tile, defaults to False.
    :raises ValueError: If the icon is an invalid choice.
    """
    main_text: Incomplete
    supporting_text: Incomplete
    label: Incomplete
    icon: Incomplete
    type: Incomplete
    unit: Incomplete
    display_compact: Incomplete
    @validate_types
    def __init__(self, label: str, main_text: str, supporting_text: str = '', icon: str = '', _type: InfographDataType = ..., unit: str | None = None, display_compact: bool = False) -> None: ...
    def to_json(self):
        """

        Returns:

        """

class Infographic(Element):
    '''An Infographic Element. 

    :param title: The title of the infographic element.
    :param description: The description of the infographic element.
    :param data: Optional list of information blocks to show, defaults to None.
    :param recommendation: Optional list of recommendation blocks to show, defaults to None.
    :param layout: This attribute is now deprecated and has no effect on how the infographic gets rendered.
    :param show_title: Whether to show the title on the page when rendered, defaults to True.
    :param show_description: Whether to show the description to the page when rendered, defaults to True.
    :param event: The CustomEvent that can be optionally added to this Infographic, defaults to None
    :raises ValueError: If no data exists in the infographic.

    **EXAMPLE:**

       .. code-block:: python

           # Imports 
           from virtualitics_sdk import InfographData, Infographic
           . . .
           # Example usage
           class ExampleStep(Step):
             def run(self, flow_metadata):
               . . . 
               pred_failure = InfographData("Predicted Failures", 
                                            "6", 
                                            "Predicted degradation failures...",
                                            "error", 
                                            InfographDataType.NEGATIVE, 
                                            display_compact=True)
               . . . 
               # multiple other InfographData elements 
               info_w_rec = Infographic("Additional Fixed Ratio Gearboxes need to be ordered",
                                        "There is sufficient time to...",
                                        [pred_failure, avg_downtime, inventory, ship_estimate], 
                                        [recommendation])
               
    The above Infographic will be displayed as: 

       .. image:: ../images/infograph_ex.png
          :align: center
          :scale: 30%
    '''
    event: Incomplete
    @validate_types
    def __init__(self, title: str = '', description: str = '', data: list[InfographData] | None = None, recommendation: list[InfographData] | None = None, layout: InfographicOrientation = ..., show_title: bool = True, show_description: bool = True, event: CustomEvent | None = None) -> None: ...
