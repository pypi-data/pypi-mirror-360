# CreateEnvironmentResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**EnvironmentSchema**](EnvironmentSchema.md) |  | 

## Example

```python
from haplohub.models.create_environment_response import CreateEnvironmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateEnvironmentResponse from a JSON string
create_environment_response_instance = CreateEnvironmentResponse.from_json(json)
# print the JSON string representation of the object
print CreateEnvironmentResponse.to_json()

# convert the object into a dict
create_environment_response_dict = create_environment_response_instance.to_dict()
# create an instance of CreateEnvironmentResponse from a dict
create_environment_response_from_dict = CreateEnvironmentResponse.from_dict(create_environment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


