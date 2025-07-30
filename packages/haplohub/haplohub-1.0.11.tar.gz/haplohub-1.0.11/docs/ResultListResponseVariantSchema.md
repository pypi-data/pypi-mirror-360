# ResultListResponseVariantSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**items** | [**List[VariantSchema]**](VariantSchema.md) |  | 

## Example

```python
from haplohub.models.result_list_response_variant_schema import ResultListResponseVariantSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultListResponseVariantSchema from a JSON string
result_list_response_variant_schema_instance = ResultListResponseVariantSchema.from_json(json)
# print the JSON string representation of the object
print ResultListResponseVariantSchema.to_json()

# convert the object into a dict
result_list_response_variant_schema_dict = result_list_response_variant_schema_instance.to_dict()
# create an instance of ResultListResponseVariantSchema from a dict
result_list_response_variant_schema_from_dict = ResultListResponseVariantSchema.from_dict(result_list_response_variant_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


