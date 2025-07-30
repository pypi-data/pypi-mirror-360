# UploadRequestResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upload_request_id** | **str** |  | 
**upload_links** | [**List[UploadLink]**](UploadLink.md) |  | 

## Example

```python
from haplohub.models.upload_request_response import UploadRequestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadRequestResponse from a JSON string
upload_request_response_instance = UploadRequestResponse.from_json(json)
# print the JSON string representation of the object
print UploadRequestResponse.to_json()

# convert the object into a dict
upload_request_response_dict = upload_request_response_instance.to_dict()
# create an instance of UploadRequestResponse from a dict
upload_request_response_from_dict = UploadRequestResponse.from_dict(upload_request_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


