# GetVariantRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sample_id** | **int** |  | 
**variants** | [**List[VariantRange]**](VariantRange.md) |  | 

## Example

```python
from haplohub.models.get_variant_request import GetVariantRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GetVariantRequest from a JSON string
get_variant_request_instance = GetVariantRequest.from_json(json)
# print the JSON string representation of the object
print GetVariantRequest.to_json()

# convert the object into a dict
get_variant_request_dict = get_variant_request_instance.to_dict()
# create an instance of GetVariantRequest from a dict
get_variant_request_from_dict = GetVariantRequest.from_dict(get_variant_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


