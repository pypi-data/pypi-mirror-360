# ResultResponseSampleFileSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**SampleFileSchema**](SampleFileSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_sample_file_schema import ResultResponseSampleFileSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseSampleFileSchema from a JSON string
result_response_sample_file_schema_instance = ResultResponseSampleFileSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseSampleFileSchema.to_json()

# convert the object into a dict
result_response_sample_file_schema_dict = result_response_sample_file_schema_instance.to_dict()
# create an instance of ResultResponseSampleFileSchema from a dict
result_response_sample_file_schema_from_dict = ResultResponseSampleFileSchema.from_dict(result_response_sample_file_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


