# CreateUploadRequestResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**UploadLinkSchema**](UploadLinkSchema.md) |  | 

## Example

```python
from haplohub.models.create_upload_request_response import CreateUploadRequestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUploadRequestResponse from a JSON string
create_upload_request_response_instance = CreateUploadRequestResponse.from_json(json)
# print the JSON string representation of the object
print CreateUploadRequestResponse.to_json()

# convert the object into a dict
create_upload_request_response_dict = create_upload_request_response_instance.to_dict()
# create an instance of CreateUploadRequestResponse from a dict
create_upload_request_response_from_dict = CreateUploadRequestResponse.from_dict(create_upload_request_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


