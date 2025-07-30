# ResultResponseApiKeySchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**ApiKeySchema**](ApiKeySchema.md) |  | 

## Example

```python
from haplohub.models.result_response_api_key_schema import ResultResponseApiKeySchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseApiKeySchema from a JSON string
result_response_api_key_schema_instance = ResultResponseApiKeySchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseApiKeySchema.to_json()

# convert the object into a dict
result_response_api_key_schema_dict = result_response_api_key_schema_instance.to_dict()
# create an instance of ResultResponseApiKeySchema from a dict
result_response_api_key_schema_from_dict = ResultResponseApiKeySchema.from_dict(result_response_api_key_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


