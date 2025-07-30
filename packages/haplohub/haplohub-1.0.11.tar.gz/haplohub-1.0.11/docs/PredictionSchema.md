# PredictionSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | [**PredictionStatus**](PredictionStatus.md) |  | 
**submitted_at** | **datetime** |  | 
**run_at** | **datetime** |  | 

## Example

```python
from haplohub.models.prediction_schema import PredictionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PredictionSchema from a JSON string
prediction_schema_instance = PredictionSchema.from_json(json)
# print the JSON string representation of the object
print PredictionSchema.to_json()

# convert the object into a dict
prediction_schema_dict = prediction_schema_instance.to_dict()
# create an instance of PredictionSchema from a dict
prediction_schema_from_dict = PredictionSchema.from_dict(prediction_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


