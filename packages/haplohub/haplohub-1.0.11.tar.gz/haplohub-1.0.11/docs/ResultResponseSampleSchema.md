# ResultResponseSampleSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**SampleSchema**](SampleSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_sample_schema import ResultResponseSampleSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseSampleSchema from a JSON string
result_response_sample_schema_instance = ResultResponseSampleSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseSampleSchema.to_json()

# convert the object into a dict
result_response_sample_schema_dict = result_response_sample_schema_instance.to_dict()
# create an instance of ResultResponseSampleSchema from a dict
result_response_sample_schema_from_dict = ResultResponseSampleSchema.from_dict(result_response_sample_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


