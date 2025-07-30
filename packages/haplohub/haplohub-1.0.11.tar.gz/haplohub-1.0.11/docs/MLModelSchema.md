# MLModelSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | 
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.ml_model_schema import MLModelSchema

# TODO update the JSON string below
json = "{}"
# create an instance of MLModelSchema from a JSON string
ml_model_schema_instance = MLModelSchema.from_json(json)
# print the JSON string representation of the object
print MLModelSchema.to_json()

# convert the object into a dict
ml_model_schema_dict = ml_model_schema_instance.to_dict()
# create an instance of MLModelSchema from a dict
ml_model_schema_from_dict = MLModelSchema.from_dict(ml_model_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


