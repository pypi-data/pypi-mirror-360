# UpdateSampleRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sample_id** | **str** |  | [optional] 
**patient_id** | **str** |  | [optional] 

## Example

```python
from haplohub.models.update_sample_request import UpdateSampleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSampleRequest from a JSON string
update_sample_request_instance = UpdateSampleRequest.from_json(json)
# print the JSON string representation of the object
print UpdateSampleRequest.to_json()

# convert the object into a dict
update_sample_request_dict = update_sample_request_instance.to_dict()
# create an instance of UpdateSampleRequest from a dict
update_sample_request_from_dict = UpdateSampleRequest.from_dict(update_sample_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


