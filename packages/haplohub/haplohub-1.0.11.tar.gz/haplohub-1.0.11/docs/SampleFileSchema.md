# SampleFileSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**filename** | **str** |  | 
**file_size** | **int** |  | 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.sample_file_schema import SampleFileSchema

# TODO update the JSON string below
json = "{}"
# create an instance of SampleFileSchema from a JSON string
sample_file_schema_instance = SampleFileSchema.from_json(json)
# print the JSON string representation of the object
print SampleFileSchema.to_json()

# convert the object into a dict
sample_file_schema_dict = sample_file_schema_instance.to_dict()
# create an instance of SampleFileSchema from a dict
sample_file_schema_from_dict = SampleFileSchema.from_dict(sample_file_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


