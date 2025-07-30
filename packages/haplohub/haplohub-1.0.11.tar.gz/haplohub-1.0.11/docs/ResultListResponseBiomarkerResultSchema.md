# ResultListResponseBiomarkerResultSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**items** | [**List[BiomarkerResultSchema]**](BiomarkerResultSchema.md) |  | 

## Example

```python
from haplohub.models.result_list_response_biomarker_result_schema import ResultListResponseBiomarkerResultSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultListResponseBiomarkerResultSchema from a JSON string
result_list_response_biomarker_result_schema_instance = ResultListResponseBiomarkerResultSchema.from_json(json)
# print the JSON string representation of the object
print ResultListResponseBiomarkerResultSchema.to_json()

# convert the object into a dict
result_list_response_biomarker_result_schema_dict = result_list_response_biomarker_result_schema_instance.to_dict()
# create an instance of ResultListResponseBiomarkerResultSchema from a dict
result_list_response_biomarker_result_schema_from_dict = ResultListResponseBiomarkerResultSchema.from_dict(result_list_response_biomarker_result_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


