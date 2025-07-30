# CreateSampleRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sample_id** | **str** |  | [optional] 
**patient_id** | **str** |  | [optional] 

## Example

```python
from haplohub.models.create_sample_request import CreateSampleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateSampleRequest from a JSON string
create_sample_request_instance = CreateSampleRequest.from_json(json)
# print the JSON string representation of the object
print CreateSampleRequest.to_json()

# convert the object into a dict
create_sample_request_dict = create_sample_request_instance.to_dict()
# create an instance of CreateSampleRequest from a dict
create_sample_request_from_dict = CreateSampleRequest.from_dict(create_sample_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


