from predict_backend.validation.type_validation import validate_types
from virtualitics_sdk.elements.element import Element as Element, ElementType as ElementType

class RichText(Element):
    '''A Rich Text Element. 
    
    :param content: The value inside the rich text element
    :param border: whether to surround the text with a border, defaults to False.
    :param title: The title of the element, defaults to \'\'.
    :param description: The element\'s description, defaults to \'\'.
    :param show_title: whether to show the title on the page when rendered, defaults to True.
    :param show_description: whether to show the description to the page when rendered, defaults to True.

    **EXAMPLE:**

       .. code-block:: python
           
           # Imports 
           from virtualitics_sdk import RichText
           . . .
           # Example usage
           class ExampleStep(Step):
             def run(self, flow_metadata):
               . . . 
               new_rich_text_1 = RichText("""
                    The usual [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
                    does not cover some of the more advanced Markdown tricks, but here
                    is one. You can combine verbatim HTML with your Markdown. 
                    This is particularly useful for tables.
                    Notice that with **empty separating lines** we can use Markdown inside HTML:

                    <table>
                    <tr>
                    <th>Json 1</th>
                    <th>Markdown</th>
                    </tr>
                    <tr>
                    <td>
                    <pre>
                    "id": 1,
                    "username": "joe",
                    "email": "joe@example.com",
                    "order_id": "3544fc0"
                    </pre>
                    </td>
                    <td>


                    "id": 5,
                    "username": "mary",
                    "email": "mary@example.com",
                    "order_id": "f7177da"
                    </td>
                    </tr>
                    </table>""", border=False)

    The above RichText will be displayed as: 
    
       .. image:: ../images/rich_text_ex.png
          :align: center
          :scale: 35%

    '''
    @validate_types
    def __init__(self, content: str, border: bool = False, title: str = '', description: str = '', show_title: bool = True, show_description: bool = True) -> None: ...
