# PushModelRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | 

## Example

```python
from haplohub.models.push_model_request import PushModelRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PushModelRequest from a JSON string
push_model_request_instance = PushModelRequest.from_json(json)
# print the JSON string representation of the object
print PushModelRequest.to_json()

# convert the object into a dict
push_model_request_dict = push_model_request_instance.to_dict()
# create an instance of PushModelRequest from a dict
push_model_request_from_dict = PushModelRequest.from_dict(push_model_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


