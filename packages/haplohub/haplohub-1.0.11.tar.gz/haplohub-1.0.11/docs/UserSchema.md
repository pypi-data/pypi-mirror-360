# UserSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 

## Example

```python
from haplohub.models.user_schema import UserSchema

# TODO update the JSON string below
json = "{}"
# create an instance of UserSchema from a JSON string
user_schema_instance = UserSchema.from_json(json)
# print the JSON string representation of the object
print UserSchema.to_json()

# convert the object into a dict
user_schema_dict = user_schema_instance.to_dict()
# create an instance of UserSchema from a dict
user_schema_from_dict = UserSchema.from_dict(user_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


