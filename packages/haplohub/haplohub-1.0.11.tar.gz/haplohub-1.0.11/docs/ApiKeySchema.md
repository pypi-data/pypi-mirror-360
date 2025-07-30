# ApiKeySchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**masked_key** | **str** |  | 
**key** | **str** |  | [optional] 
**created_at** | **datetime** |  | 

## Example

```python
from haplohub.models.api_key_schema import ApiKeySchema

# TODO update the JSON string below
json = "{}"
# create an instance of ApiKeySchema from a JSON string
api_key_schema_instance = ApiKeySchema.from_json(json)
# print the JSON string representation of the object
print ApiKeySchema.to_json()

# convert the object into a dict
api_key_schema_dict = api_key_schema_instance.to_dict()
# create an instance of ApiKeySchema from a dict
api_key_schema_from_dict = ApiKeySchema.from_dict(api_key_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


