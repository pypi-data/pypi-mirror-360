# CohortSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | 
**read_only** | **bool** |  | [optional] [default to False]
**description** | **str** |  | 
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.cohort_schema import CohortSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CohortSchema from a JSON string
cohort_schema_instance = CohortSchema.from_json(json)
# print the JSON string representation of the object
print CohortSchema.to_json()

# convert the object into a dict
cohort_schema_dict = cohort_schema_instance.to_dict()
# create an instance of CohortSchema from a dict
cohort_schema_from_dict = CohortSchema.from_dict(cohort_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


