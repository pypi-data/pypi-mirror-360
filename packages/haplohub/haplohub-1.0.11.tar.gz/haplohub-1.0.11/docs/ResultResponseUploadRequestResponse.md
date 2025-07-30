# ResultResponseUploadRequestResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**UploadRequestResponse**](UploadRequestResponse.md) |  | 

## Example

```python
from haplohub.models.result_response_upload_request_response import ResultResponseUploadRequestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseUploadRequestResponse from a JSON string
result_response_upload_request_response_instance = ResultResponseUploadRequestResponse.from_json(json)
# print the JSON string representation of the object
print ResultResponseUploadRequestResponse.to_json()

# convert the object into a dict
result_response_upload_request_response_dict = result_response_upload_request_response_instance.to_dict()
# create an instance of ResultResponseUploadRequestResponse from a dict
result_response_upload_request_response_from_dict = ResultResponseUploadRequestResponse.from_dict(result_response_upload_request_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


