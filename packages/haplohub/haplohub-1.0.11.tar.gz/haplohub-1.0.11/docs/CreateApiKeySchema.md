# CreateApiKeySchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from haplohub.models.create_api_key_schema import CreateApiKeySchema

# TODO update the JSON string below
json = "{}"
# create an instance of CreateApiKeySchema from a JSON string
create_api_key_schema_instance = CreateApiKeySchema.from_json(json)
# print the JSON string representation of the object
print CreateApiKeySchema.to_json()

# convert the object into a dict
create_api_key_schema_dict = create_api_key_schema_instance.to_dict()
# create an instance of CreateApiKeySchema from a dict
create_api_key_schema_from_dict = CreateApiKeySchema.from_dict(create_api_key_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


