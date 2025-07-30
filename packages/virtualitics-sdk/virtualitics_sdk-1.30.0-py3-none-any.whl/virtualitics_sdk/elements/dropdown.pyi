from _typeshed import Incomplete
from predict_backend.validation.type_validation import validate_types
from virtualitics_sdk.elements.element import ElementType as ElementType, InputElement as InputElement

class Dropdown(InputElement):
    '''A Dropdown Input element.

    :param options: The options in the dropdown menu.
    :param selected: The option the user selected, defaults to [].
    :param include_nulls_visible: whether null values will be visible, defaults to True.
    :param include_nulls_value: whether to include null values, defaults to False.
    :param multiselect: whether the user can select multiple values, defaults to False.
    :param title: The title of the element, defaults to \'\'.
    :param description: The element\'s description, defaults to \'\'.
    :param show_title: whether to show the title on the page when rendered, defaults to True.
    :param show_description: whether to show the description to the page when rendered, defaults to True.
    :param required: whether a selection needs to be submitted for the step to continue, defaults to True
    :param label: The label of the element, defaults to \'\'.
    :param placeholder: The placeholder of the element, defaults to \'\'.
    :param max_selections: The maximum number of selections that can be made at one time, no limit set by default. This value must be greater than zero.

    **EXAMPLE**

       .. code-block:: python

           # Imports
           from virtualitics_sdk import Dropdown
           . . .
           # Example usage
           class ExStep(Step):
             def run(self, flow_metadata):
               . . .
               dropdown_options = [\'a\', \'b\', \'c\']
               single_selection_dropdown = Dropdown(options=dropdown_options, 
                                                    multiselect=False, 
                                                    title="Single Selection Dropdown", 
                                                    selected=[\'a\'])
               multiple_selection_dropdown = Dropdown(options=dropdown_options, 
                                                      multiselect=True, 
                                                      title="Multiple Selection Dropdown", 
                                                      selected=[\'a\', \'b\'])
               
    The above single and multi Dropdown examples will be displayed as: 

       .. image:: ../images/dropdown_ex.png
          :align: center
    '''
    required: Incomplete
    @validate_types
    def __init__(self, options: list[str | int | float], selected: list[str | int | float] | None = None, include_nulls_visible: bool = True, include_nulls_value: bool = False, multiselect: bool = False, title: str = '', description: str = '', show_title: bool = True, show_description: bool = True, required: bool = True, label: str = '', placeholder: str = '', max_selections: int | None = None) -> None: ...
    def get_value(self) -> str | list[str]: ...
    def update_from_input_parameters(self) -> None: ...

class SingleDropdown(Dropdown):
    '''A  Single Dropdown Input element.

    :param options: The options in the dropdown menu.
    :param selected: The option the user selected, defaults to None.
    :param include_nulls_visible: whether null values will be visible, defaults to True.
    :param include_nulls_value: whether to include null values, defaults to False.
    :param title: The title of the element, defaults to \'\'.
    :param description: The element\'s description, defaults to \'\'.
    :param show_title: whether to show the title on the page when rendered, defaults to True.
    :param show_description: whether to show the description to the page when rendered, defaults to True.
    :param required: whether a selection needs to be submitted for the step to continue, defaults to True
    :param label: The label of the element, defaults to \'\'.
    :param placeholder: The placeholder of the element, defaults to \'\'.

    **EXAMPLE**

       .. code-block:: python

           # Imports
           from virtualitics_sdk import SingleDropdown
           . . .
           # Example usage
           class ExStep(Step):
             def run(self, flow_metadata):
               . . .
               dropdown_options = [\'a\', \'b\', \'c\']
               single_selection_dropdown = SingleDropdown(options=dropdown_options,
                                                                     title="Single Selection Dropdown",
                                                                     selected=\'a\')

    '''
    def __init__(self, options: list[str | int | float], selected: int | float | str | None = None, include_nulls_visible: bool = True, include_nulls_value: bool = False, title: str = '', description: str = '', show_title: bool = True, show_description: bool = True, required: bool = True, label: str = '', placeholder: str = '') -> None: ...

class MultiDropdown(Dropdown):
    '''A Multi Dropdown Input element.

    :param options: The options in the dropdown menu.
    :param selected: The option the user selected, defaults to [].
    :param include_nulls_visible: whether null values will be visible, defaults to True.
    :param include_nulls_value: whether to include null values, defaults to False.
    :param title: The title of the element, defaults to \'\'.
    :param description: The element\'s description, defaults to \'\'.
    :param show_title: whether to show the title on the page when rendered, defaults to True.
    :param show_description: whether to show the description to the page when rendered, defaults to True.
    :param required: whether a selection needs to be submitted for the step to continue, defaults to True
    :param label: The label of the element, defaults to \'\'.
    :param placeholder: The placeholder of the element, defaults to \'\'.
    :param max_selections: The maximum number of selections that can be made at one time, no limit set by default. This value must be greater than zero.

    **EXAMPLE**

       .. code-block:: python

           # Imports
           from virtualitics_sdk import MultiDropdown
           . . .
           # Example usage
           class ExStep(Step):
             def run(self, flow_metadata):
               . . .
               dropdown_options = [\'a\', \'b\', \'c\']
               multiple_selection_dropdown = MultiDropdown(options=dropdown_options,
                                                                   title="Multiple Selection Dropdown",
                                                                   selected=[\'a\', \'b\'])
    '''
    def __init__(self, options: list[str | int | float], selected: list[str | int | float] | None = None, include_nulls_visible: bool = True, include_nulls_value: bool = False, title: str = '', description: str = '', show_title: bool = True, show_description: bool = True, required: bool = True, label: str = '', placeholder: str = '', max_selections: int | None = None) -> None: ...
