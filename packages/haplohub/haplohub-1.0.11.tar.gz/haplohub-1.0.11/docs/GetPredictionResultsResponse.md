# GetPredictionResultsResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**PredictionResultsSchema**](PredictionResultsSchema.md) |  | 

## Example

```python
from haplohub.models.get_prediction_results_response import GetPredictionResultsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPredictionResultsResponse from a JSON string
get_prediction_results_response_instance = GetPredictionResultsResponse.from_json(json)
# print the JSON string representation of the object
print GetPredictionResultsResponse.to_json()

# convert the object into a dict
get_prediction_results_response_dict = get_prediction_results_response_instance.to_dict()
# create an instance of GetPredictionResultsResponse from a dict
get_prediction_results_response_from_dict = GetPredictionResultsResponse.from_dict(get_prediction_results_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


