# TenantSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **int** |  | 
**org_external_id** | **str** |  | 

## Example

```python
from haplohub.models.tenant_schema import TenantSchema

# TODO update the JSON string below
json = "{}"
# create an instance of TenantSchema from a JSON string
tenant_schema_instance = TenantSchema.from_json(json)
# print the JSON string representation of the object
print TenantSchema.to_json()

# convert the object into a dict
tenant_schema_dict = tenant_schema_instance.to_dict()
# create an instance of TenantSchema from a dict
tenant_schema_from_dict = TenantSchema.from_dict(tenant_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


