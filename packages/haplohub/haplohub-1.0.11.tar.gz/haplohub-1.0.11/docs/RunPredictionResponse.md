# RunPredictionResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**PredictionSchema**](PredictionSchema.md) |  | 

## Example

```python
from haplohub.models.run_prediction_response import RunPredictionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RunPredictionResponse from a JSON string
run_prediction_response_instance = RunPredictionResponse.from_json(json)
# print the JSON string representation of the object
print RunPredictionResponse.to_json()

# convert the object into a dict
run_prediction_response_dict = run_prediction_response_instance.to_dict()
# create an instance of RunPredictionResponse from a dict
run_prediction_response_from_dict = RunPredictionResponse.from_dict(run_prediction_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


