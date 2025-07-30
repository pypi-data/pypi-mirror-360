# PaginatedResponsePredictionSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[PredictionSchema]**](PredictionSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_prediction_schema import PaginatedResponsePredictionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponsePredictionSchema from a JSON string
paginated_response_prediction_schema_instance = PaginatedResponsePredictionSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponsePredictionSchema.to_json()

# convert the object into a dict
paginated_response_prediction_schema_dict = paginated_response_prediction_schema_instance.to_dict()
# create an instance of PaginatedResponsePredictionSchema from a dict
paginated_response_prediction_schema_from_dict = PaginatedResponsePredictionSchema.from_dict(paginated_response_prediction_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


