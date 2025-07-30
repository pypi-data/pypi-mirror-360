# VariantRange


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accession** | **str** |  | 
**start** | **int** |  | 
**end** | **int** |  | 
**reference** | **str** |  | [optional] 
**alternate** | **str** |  | [optional] 

## Example

```python
from haplohub.models.variant_range import VariantRange

# TODO update the JSON string below
json = "{}"
# create an instance of VariantRange from a JSON string
variant_range_instance = VariantRange.from_json(json)
# print the JSON string representation of the object
print VariantRange.to_json()

# convert the object into a dict
variant_range_dict = variant_range_instance.to_dict()
# create an instance of VariantRange from a dict
variant_range_from_dict = VariantRange.from_dict(variant_range_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


