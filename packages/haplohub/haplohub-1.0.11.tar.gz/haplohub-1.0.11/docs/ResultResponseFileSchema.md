# ResultResponseFileSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**FileSchema**](FileSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_file_schema import ResultResponseFileSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseFileSchema from a JSON string
result_response_file_schema_instance = ResultResponseFileSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseFileSchema.to_json()

# convert the object into a dict
result_response_file_schema_dict = result_response_file_schema_instance.to_dict()
# create an instance of ResultResponseFileSchema from a dict
result_response_file_schema_from_dict = ResultResponseFileSchema.from_dict(result_response_file_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


