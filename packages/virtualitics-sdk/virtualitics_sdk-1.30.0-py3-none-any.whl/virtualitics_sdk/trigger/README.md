### How to Trigger a Headless App (and pass User Inputs)

Example Code:

```python
from predict_backend.page.utils import trigger_flow_execution
from predict_backend.store.store_interface import StoreInterface

# create a store interface to the source app (the app where this trigger_flow_execution function will be
# called from, this is needed to pass paramters to the new app that will be created
flow_metadata = {"flow_id": "1234", "user": "me"}
store_interface = StoreInterface(**flow_metadata)

# pass the name of the app being triggered, the store interface and then any input_parameters
trigger_flow_execution(flow_name="TriggerFlowTest",
                       store_interface=store_interface,
                       input_parameters={"steps": {
                           "DataUpload": {
                               "Dropdown One": {"value": "A", "description": "", "card_title": "User Input Card"},
                               "Dropdown Two": {"value": "B", "card_title": "User Input Card"}}}})
```

Any input parameters will be used to supply default values to the inputs of a specific step. The input parameters have a
syntax as follows:

```json
{
  "steps": {
    "{step_name}": {
      "{element_title}": {
        "value": "{value to pass to element's update_from_user_input function}",
        "description": "{optional description}",
        "card_title": "{title of the card that contains this element}"
      }
    }
  }
}
```

So you must provide the step name and the card title where the element is found, the element's title as well as the
value
to pass to the element's update_from_user_input function (this is the function that is called when a user interacts
with an input element and changes its value)
