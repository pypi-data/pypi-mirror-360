# FileDirSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**location** | **str** |  | 
**dirs** | [**List[DirSchema]**](DirSchema.md) |  | 
**files** | [**List[FileSchema]**](FileSchema.md) |  | 

## Example

```python
from haplohub.models.file_dir_schema import FileDirSchema

# TODO update the JSON string below
json = "{}"
# create an instance of FileDirSchema from a JSON string
file_dir_schema_instance = FileDirSchema.from_json(json)
# print the JSON string representation of the object
print FileDirSchema.to_json()

# convert the object into a dict
file_dir_schema_dict = file_dir_schema_instance.to_dict()
# create an instance of FileDirSchema from a dict
file_dir_schema_from_dict = FileDirSchema.from_dict(file_dir_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


