# ResultResponseDirSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**DirSchema**](DirSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_dir_schema import ResultResponseDirSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseDirSchema from a JSON string
result_response_dir_schema_instance = ResultResponseDirSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseDirSchema.to_json()

# convert the object into a dict
result_response_dir_schema_dict = result_response_dir_schema_instance.to_dict()
# create an instance of ResultResponseDirSchema from a dict
result_response_dir_schema_from_dict = ResultResponseDirSchema.from_dict(result_response_dir_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


