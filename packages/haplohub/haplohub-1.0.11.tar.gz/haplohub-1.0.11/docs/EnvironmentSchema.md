# EnvironmentSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_current** | **bool** |  | [optional] [default to False]
**id** | **int** |  | [optional] 
**name** | **str** |  | 
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.environment_schema import EnvironmentSchema

# TODO update the JSON string below
json = "{}"
# create an instance of EnvironmentSchema from a JSON string
environment_schema_instance = EnvironmentSchema.from_json(json)
# print the JSON string representation of the object
print EnvironmentSchema.to_json()

# convert the object into a dict
environment_schema_dict = environment_schema_instance.to_dict()
# create an instance of EnvironmentSchema from a dict
environment_schema_from_dict = EnvironmentSchema.from_dict(environment_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


