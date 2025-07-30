# PushCredentials


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registry_host** | **str** |  | 
**image_path** | **str** |  | 
**push_token** | **str** |  | 

## Example

```python
from haplohub.models.push_credentials import PushCredentials

# TODO update the JSON string below
json = "{}"
# create an instance of PushCredentials from a JSON string
push_credentials_instance = PushCredentials.from_json(json)
# print the JSON string representation of the object
print PushCredentials.to_json()

# convert the object into a dict
push_credentials_dict = push_credentials_instance.to_dict()
# create an instance of PushCredentials from a dict
push_credentials_from_dict = PushCredentials.from_dict(push_credentials_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


