# ListFilesRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**recursive** | **bool** |  | [optional] [default to True]
**sample_id** | **str** |  | [optional] 
**member_id** | **str** |  | [optional] 
**path** | **str** |  | [optional] 

## Example

```python
from haplohub.models.list_files_request import ListFilesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListFilesRequest from a JSON string
list_files_request_instance = ListFilesRequest.from_json(json)
# print the JSON string representation of the object
print ListFilesRequest.to_json()

# convert the object into a dict
list_files_request_dict = list_files_request_instance.to_dict()
# create an instance of ListFilesRequest from a dict
list_files_request_from_dict = ListFilesRequest.from_dict(list_files_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


