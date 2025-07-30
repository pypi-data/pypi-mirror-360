# SampleSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**member_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**sample_id** | **str** |  | [optional] 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.sample_schema import SampleSchema

# TODO update the JSON string below
json = "{}"
# create an instance of SampleSchema from a JSON string
sample_schema_instance = SampleSchema.from_json(json)
# print the JSON string representation of the object
print SampleSchema.to_json()

# convert the object into a dict
sample_schema_dict = sample_schema_instance.to_dict()
# create an instance of SampleSchema from a dict
sample_schema_from_dict = SampleSchema.from_dict(sample_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


