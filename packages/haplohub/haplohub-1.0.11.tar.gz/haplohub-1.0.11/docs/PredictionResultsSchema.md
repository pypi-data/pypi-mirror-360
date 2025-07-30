# PredictionResultsSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prediction_id** | **str** |  | 
**results** | **object** |  | 

## Example

```python
from haplohub.models.prediction_results_schema import PredictionResultsSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PredictionResultsSchema from a JSON string
prediction_results_schema_instance = PredictionResultsSchema.from_json(json)
# print the JSON string representation of the object
print PredictionResultsSchema.to_json()

# convert the object into a dict
prediction_results_schema_dict = prediction_results_schema_instance.to_dict()
# create an instance of PredictionResultsSchema from a dict
prediction_results_schema_from_dict = PredictionResultsSchema.from_dict(prediction_results_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


