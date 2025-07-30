# BiomarkerResultSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order** | [**OrderSchema**](OrderSchema.md) |  | 
**results** | [**List[ResultSchema]**](ResultSchema.md) |  | 

## Example

```python
from haplohub.models.biomarker_result_schema import BiomarkerResultSchema

# TODO update the JSON string below
json = "{}"
# create an instance of BiomarkerResultSchema from a JSON string
biomarker_result_schema_instance = BiomarkerResultSchema.from_json(json)
# print the JSON string representation of the object
print BiomarkerResultSchema.to_json()

# convert the object into a dict
biomarker_result_schema_dict = biomarker_result_schema_instance.to_dict()
# create an instance of BiomarkerResultSchema from a dict
biomarker_result_schema_from_dict = BiomarkerResultSchema.from_dict(biomarker_result_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


