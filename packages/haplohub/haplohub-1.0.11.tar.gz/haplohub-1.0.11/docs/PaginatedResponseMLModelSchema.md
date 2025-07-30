# PaginatedResponseMLModelSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[MLModelSchema]**](MLModelSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_ml_model_schema import PaginatedResponseMLModelSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseMLModelSchema from a JSON string
paginated_response_ml_model_schema_instance = PaginatedResponseMLModelSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseMLModelSchema.to_json()

# convert the object into a dict
paginated_response_ml_model_schema_dict = paginated_response_ml_model_schema_instance.to_dict()
# create an instance of PaginatedResponseMLModelSchema from a dict
paginated_response_ml_model_schema_from_dict = PaginatedResponseMLModelSchema.from_dict(paginated_response_ml_model_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


