# ListFilesFilter


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**recursive** | **bool** |  | [optional] [default to True]
**sample_id** | **str** |  | [optional] 
**member_id** | **str** |  | [optional] 
**path** | **str** |  | [optional] 

## Example

```python
from haplohub.models.list_files_filter import ListFilesFilter

# TODO update the JSON string below
json = "{}"
# create an instance of ListFilesFilter from a JSON string
list_files_filter_instance = ListFilesFilter.from_json(json)
# print the JSON string representation of the object
print ListFilesFilter.to_json()

# convert the object into a dict
list_files_filter_dict = list_files_filter_instance.to_dict()
# create an instance of ListFilesFilter from a dict
list_files_filter_from_dict = ListFilesFilter.from_dict(list_files_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


