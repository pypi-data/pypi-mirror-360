# RunPredictionRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | 
**model_id** | **str** |  | 

## Example

```python
from haplohub.models.run_prediction_request import RunPredictionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RunPredictionRequest from a JSON string
run_prediction_request_instance = RunPredictionRequest.from_json(json)
# print the JSON string representation of the object
print RunPredictionRequest.to_json()

# convert the object into a dict
run_prediction_request_dict = run_prediction_request_instance.to_dict()
# create an instance of RunPredictionRequest from a dict
run_prediction_request_from_dict = RunPredictionRequest.from_dict(run_prediction_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


