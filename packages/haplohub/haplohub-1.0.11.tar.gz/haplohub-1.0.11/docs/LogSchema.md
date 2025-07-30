# LogSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**timestamp** | **datetime** |  | 
**tenant** | [**TenantSchema**](TenantSchema.md) |  | 
**auth** | [**AuthSchema**](AuthSchema.md) |  | 
**request** | [**RequestSchema**](RequestSchema.md) |  | 
**response** | [**ResponseSchema**](ResponseSchema.md) |  | 

## Example

```python
from haplohub.models.log_schema import LogSchema

# TODO update the JSON string below
json = "{}"
# create an instance of LogSchema from a JSON string
log_schema_instance = LogSchema.from_json(json)
# print the JSON string representation of the object
print LogSchema.to_json()

# convert the object into a dict
log_schema_dict = log_schema_instance.to_dict()
# create an instance of LogSchema from a dict
log_schema_from_dict = LogSchema.from_dict(log_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


