# HgvsSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hgvs** | **str** |  | 
**found** | **bool** |  | 
**dosage** | **int** |  | [optional] 

## Example

```python
from haplohub.models.hgvs_schema import HgvsSchema

# TODO update the JSON string below
json = "{}"
# create an instance of HgvsSchema from a JSON string
hgvs_schema_instance = HgvsSchema.from_json(json)
# print the JSON string representation of the object
print HgvsSchema.to_json()

# convert the object into a dict
hgvs_schema_dict = hgvs_schema_instance.to_dict()
# create an instance of HgvsSchema from a dict
hgvs_schema_from_dict = HgvsSchema.from_dict(hgvs_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


