# ListModelsRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page** | **int** |  | [optional] [default to 1]
**page_size** | **int** |  | [optional] [default to 10]
**search** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from haplohub.models.list_models_request import ListModelsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListModelsRequest from a JSON string
list_models_request_instance = ListModelsRequest.from_json(json)
# print the JSON string representation of the object
print ListModelsRequest.to_json()

# convert the object into a dict
list_models_request_dict = list_models_request_instance.to_dict()
# create an instance of ListModelsRequest from a dict
list_models_request_from_dict = ListModelsRequest.from_dict(list_models_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


