from datetime import datetime
from predict_backend.validation.type_validation import validate_types
from virtualitics_sdk.elements.element import ElementType as ElementType, InputElement as InputElement

class DateTimeRange(InputElement):
    '''A DateTimeRange Input element. 

    :param min_range: The minimum date in the range.
    :param max_range: The maximum date in the range.
    :param min_selection: The mimumum selected date. Defaults to the min_range value.
    :param max_selection: The maximum selected date. Defaults to max_range value.
    :param include_nulls_visible: whether null values will be visible, defaults to True.
    :param include_nulls_value: whether to include null values, defaults to False.
    :param title: The title of the element, defaults to \'\'.
    :param description: The element\'s description, defaults to \'\'.
    :param show_title: whether to show the title on the page when rendered, defaults to True.
    :param show_description: whether to show the description to the page when rendered, defaults to True.
    :param label: The label of the element, defaults to \'\'.
    :param placeholder: The placeholder of the element, defaults to \'\'.
    
    **EXAMPLE:**

       .. code-block:: python

           # Imports 
           from virtualitics_sdk import DateTimeRange
           . . .
           # Example usage
           class LandingStep(Step):
             def run(self, flow_metadata):
               . . . 
               date_range = DateTimeRange(datetime.today().replace(year=2000),
                                          datetime.today().
                                          replace(year=2020), 
                                          title="Date Time Range", 
                                          description= "Here\'s a datetime range 
                                                        from the beginning of the 
                                                        month to now.")

    The above DateTimeRange example will be displayed as: 

       .. image:: ../images/date_time_range_ex.png
          :align: center
    '''
    time_format: str
    @validate_types
    def __init__(self, min_range: datetime, max_range: datetime, min_selection: datetime | None = None, max_selection: datetime | None = None, include_nulls_visible: bool = True, include_nulls_value: bool = False, title: str = '', description: str = '', show_title: bool = True, show_description: bool = True, label: str = '', placeholder: str = '', timezone: str = 'UTC') -> None: ...
    def get_value(self):
        """Get the value of an element. If the user has interacted with the value, the default
           will be updated.
        """
