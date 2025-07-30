# ResultListResponseHgvsSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**items** | [**List[HgvsSchema]**](HgvsSchema.md) |  | 

## Example

```python
from haplohub.models.result_list_response_hgvs_schema import ResultListResponseHgvsSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultListResponseHgvsSchema from a JSON string
result_list_response_hgvs_schema_instance = ResultListResponseHgvsSchema.from_json(json)
# print the JSON string representation of the object
print ResultListResponseHgvsSchema.to_json()

# convert the object into a dict
result_list_response_hgvs_schema_dict = result_list_response_hgvs_schema_instance.to_dict()
# create an instance of ResultListResponseHgvsSchema from a dict
result_list_response_hgvs_schema_from_dict = ResultListResponseHgvsSchema.from_dict(result_list_response_hgvs_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


