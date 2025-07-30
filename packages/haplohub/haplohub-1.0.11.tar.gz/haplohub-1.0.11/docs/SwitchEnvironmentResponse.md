# SwitchEnvironmentResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**EnvironmentSchema**](EnvironmentSchema.md) |  | 

## Example

```python
from haplohub.models.switch_environment_response import SwitchEnvironmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SwitchEnvironmentResponse from a JSON string
switch_environment_response_instance = SwitchEnvironmentResponse.from_json(json)
# print the JSON string representation of the object
print SwitchEnvironmentResponse.to_json()

# convert the object into a dict
switch_environment_response_dict = switch_environment_response_instance.to_dict()
# create an instance of SwitchEnvironmentResponse from a dict
switch_environment_response_from_dict = SwitchEnvironmentResponse.from_dict(switch_environment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


