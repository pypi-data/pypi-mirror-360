# PaginatedResponseAccessionSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[AccessionSchema]**](AccessionSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_accession_schema import PaginatedResponseAccessionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseAccessionSchema from a JSON string
paginated_response_accession_schema_instance = PaginatedResponseAccessionSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseAccessionSchema.to_json()

# convert the object into a dict
paginated_response_accession_schema_dict = paginated_response_accession_schema_instance.to_dict()
# create an instance of PaginatedResponseAccessionSchema from a dict
paginated_response_accession_schema_from_dict = PaginatedResponseAccessionSchema.from_dict(paginated_response_accession_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


