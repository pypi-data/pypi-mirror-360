# PaginatedResponseEnvironmentSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[EnvironmentSchema]**](EnvironmentSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_environment_schema import PaginatedResponseEnvironmentSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseEnvironmentSchema from a JSON string
paginated_response_environment_schema_instance = PaginatedResponseEnvironmentSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseEnvironmentSchema.to_json()

# convert the object into a dict
paginated_response_environment_schema_dict = paginated_response_environment_schema_instance.to_dict()
# create an instance of PaginatedResponseEnvironmentSchema from a dict
paginated_response_environment_schema_from_dict = PaginatedResponseEnvironmentSchema.from_dict(paginated_response_environment_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


