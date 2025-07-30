# GetPredictionResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**PredictionSchema**](PredictionSchema.md) |  | 

## Example

```python
from haplohub.models.get_prediction_response import GetPredictionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPredictionResponse from a JSON string
get_prediction_response_instance = GetPredictionResponse.from_json(json)
# print the JSON string representation of the object
print GetPredictionResponse.to_json()

# convert the object into a dict
get_prediction_response_dict = get_prediction_response_instance.to_dict()
# create an instance of GetPredictionResponse from a dict
get_prediction_response_from_dict = GetPredictionResponse.from_dict(get_prediction_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


