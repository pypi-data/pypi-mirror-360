# HgvsDosageSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sample_id** | **str** |  | 
**description** | **str** |  | 
**dosage** | **int** |  | 

## Example

```python
from haplohub.models.hgvs_dosage_schema import HgvsDosageSchema

# TODO update the JSON string below
json = "{}"
# create an instance of HgvsDosageSchema from a JSON string
hgvs_dosage_schema_instance = HgvsDosageSchema.from_json(json)
# print the JSON string representation of the object
print HgvsDosageSchema.to_json()

# convert the object into a dict
hgvs_dosage_schema_dict = hgvs_dosage_schema_instance.to_dict()
# create an instance of HgvsDosageSchema from a dict
hgvs_dosage_schema_from_dict = HgvsDosageSchema.from_dict(hgvs_dosage_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


