from predict_backend.validation.type_validation import validate_types
from virtualitics_sdk.elements.element import ElementType as ElementType, InputElement as InputElement

class TextInput(InputElement):
    '''A Text Input element.
    
    :param value: The inputted text, defaults to \'\'.
    :param title: The title of the element, defaults to \'\'.
    :param description: The element\'s description, defaults to \'\'.
    :param show_title: whether to show the title on the page when rendered, defaults to True.
    :param show_description: whether to show the description to the page when rendered, defaults to True.
    :param label: The label of the element, defaults to \'\'.
    :param placeholder: The placeholder of the element, defaults to \'\'. 

    **EXAMPLE:**

       .. code-block:: python
           
           # Imports 
           from virtualitics_sdk import TextInput
           . . . 
           # Example usage
           class ExampleStep(Step):
             def run(self, flow_metadata):
               . . . 
               text_input = TextInput("Initial values can be set", 
                                      title="Text Input", 
                                      label="Some Text",
                                      description="Of course we also 
                                                   allow _open ended_ text 
                                                   input such as this.",
                                                   placeholder=\'Type Something\')

    The above TextInput will be displayed as: 
               
       .. image:: ../images/text_input_ex.png
          :align: center
    '''
    @validate_types
    def __init__(self, value: str = '', description: str = '', title: str = '', show_title: bool = True, show_description: bool = True, label: str = '', placeholder: str = '') -> None: ...
    def get_value(self) -> str: ...
