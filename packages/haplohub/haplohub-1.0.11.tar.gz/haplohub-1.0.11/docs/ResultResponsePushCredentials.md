# ResultResponsePushCredentials


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**PushCredentials**](PushCredentials.md) |  | 

## Example

```python
from haplohub.models.result_response_push_credentials import ResultResponsePushCredentials

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponsePushCredentials from a JSON string
result_response_push_credentials_instance = ResultResponsePushCredentials.from_json(json)
# print the JSON string representation of the object
print ResultResponsePushCredentials.to_json()

# convert the object into a dict
result_response_push_credentials_dict = result_response_push_credentials_instance.to_dict()
# create an instance of ResultResponsePushCredentials from a dict
result_response_push_credentials_from_dict = ResultResponsePushCredentials.from_dict(result_response_push_credentials_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


