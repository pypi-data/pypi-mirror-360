# DirSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**location** | **str** |  | 

## Example

```python
from haplohub.models.dir_schema import DirSchema

# TODO update the JSON string below
json = "{}"
# create an instance of DirSchema from a JSON string
dir_schema_instance = DirSchema.from_json(json)
# print the JSON string representation of the object
print DirSchema.to_json()

# convert the object into a dict
dir_schema_dict = dir_schema_instance.to_dict()
# create an instance of DirSchema from a dict
dir_schema_from_dict = DirSchema.from_dict(dir_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


