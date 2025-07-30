# FinishUploadingRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upload_file_request_id** | **str** |  | 
**sample_id** | **str** |  | [optional] 

## Example

```python
from haplohub.models.finish_uploading_request import FinishUploadingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FinishUploadingRequest from a JSON string
finish_uploading_request_instance = FinishUploadingRequest.from_json(json)
# print the JSON string representation of the object
print FinishUploadingRequest.to_json()

# convert the object into a dict
finish_uploading_request_dict = finish_uploading_request_instance.to_dict()
# create an instance of FinishUploadingRequest from a dict
finish_uploading_request_from_dict = FinishUploadingRequest.from_dict(finish_uploading_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


