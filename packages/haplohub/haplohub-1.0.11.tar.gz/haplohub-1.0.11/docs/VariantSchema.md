# VariantSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accession** | **str** |  | 
**position** | **int** |  | 
**id** | **str** |  | 
**reference** | **str** |  | 
**alternate** | **List[str]** |  | 
**dosage** | **int** |  | 
**is_called** | **bool** |  | 
**quality** | **float** |  | 

## Example

```python
from haplohub.models.variant_schema import VariantSchema

# TODO update the JSON string below
json = "{}"
# create an instance of VariantSchema from a JSON string
variant_schema_instance = VariantSchema.from_json(json)
# print the JSON string representation of the object
print VariantSchema.to_json()

# convert the object into a dict
variant_schema_dict = variant_schema_instance.to_dict()
# create an instance of VariantSchema from a dict
variant_schema_from_dict = VariantSchema.from_dict(variant_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


