# CreateUploadRequestRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upload_request_id** | **str** |  | 
**files** | [**List[FileInfo]**](FileInfo.md) |  | 
**file_type** | [**UploadType**](UploadType.md) |  | 
**sample_id** | **str** |  | [optional] 
**member_id** | **str** |  | [optional] 

## Example

```python
from haplohub.models.create_upload_request_request import CreateUploadRequestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUploadRequestRequest from a JSON string
create_upload_request_request_instance = CreateUploadRequestRequest.from_json(json)
# print the JSON string representation of the object
print CreateUploadRequestRequest.to_json()

# convert the object into a dict
create_upload_request_request_dict = create_upload_request_request_instance.to_dict()
# create an instance of CreateUploadRequestRequest from a dict
create_upload_request_request_from_dict = CreateUploadRequestRequest.from_dict(create_upload_request_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


