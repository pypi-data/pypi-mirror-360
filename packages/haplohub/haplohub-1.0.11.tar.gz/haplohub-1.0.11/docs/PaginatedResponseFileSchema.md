# PaginatedResponseFileSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[FileSchema]**](FileSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_file_schema import PaginatedResponseFileSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseFileSchema from a JSON string
paginated_response_file_schema_instance = PaginatedResponseFileSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseFileSchema.to_json()

# convert the object into a dict
paginated_response_file_schema_dict = paginated_response_file_schema_instance.to_dict()
# create an instance of PaginatedResponseFileSchema from a dict
paginated_response_file_schema_from_dict = PaginatedResponseFileSchema.from_dict(paginated_response_file_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


