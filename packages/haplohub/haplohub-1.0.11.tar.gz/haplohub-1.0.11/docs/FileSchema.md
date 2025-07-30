# FileSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**location** | **str** |  | 
**mime_type** | **str** |  | [optional] 
**file_size** | **int** |  | [optional] 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.file_schema import FileSchema

# TODO update the JSON string below
json = "{}"
# create an instance of FileSchema from a JSON string
file_schema_instance = FileSchema.from_json(json)
# print the JSON string representation of the object
print FileSchema.to_json()

# convert the object into a dict
file_schema_dict = file_schema_instance.to_dict()
# create an instance of FileSchema from a dict
file_schema_from_dict = FileSchema.from_dict(file_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


