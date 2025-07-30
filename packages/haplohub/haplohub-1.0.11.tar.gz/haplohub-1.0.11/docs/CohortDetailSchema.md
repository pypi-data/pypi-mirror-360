# CohortDetailSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | 
**read_only** | **bool** |  | [optional] [default to False]
**description** | **str** |  | 
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 
**samples** | [**List[SampleSchema]**](SampleSchema.md) |  | 
**files** | [**List[FileSchema]**](FileSchema.md) |  | 

## Example

```python
from haplohub.models.cohort_detail_schema import CohortDetailSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CohortDetailSchema from a JSON string
cohort_detail_schema_instance = CohortDetailSchema.from_json(json)
# print the JSON string representation of the object
print CohortDetailSchema.to_json()

# convert the object into a dict
cohort_detail_schema_dict = cohort_detail_schema_instance.to_dict()
# create an instance of CohortDetailSchema from a dict
cohort_detail_schema_from_dict = CohortDetailSchema.from_dict(cohort_detail_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


