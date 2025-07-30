# PaginatedResponseApiKeySchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[ApiKeySchema]**](ApiKeySchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_api_key_schema import PaginatedResponseApiKeySchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseApiKeySchema from a JSON string
paginated_response_api_key_schema_instance = PaginatedResponseApiKeySchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseApiKeySchema.to_json()

# convert the object into a dict
paginated_response_api_key_schema_dict = paginated_response_api_key_schema_instance.to_dict()
# create an instance of PaginatedResponseApiKeySchema from a dict
paginated_response_api_key_schema_from_dict = PaginatedResponseApiKeySchema.from_dict(paginated_response_api_key_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


