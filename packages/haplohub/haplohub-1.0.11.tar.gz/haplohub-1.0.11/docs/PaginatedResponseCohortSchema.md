# PaginatedResponseCohortSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[CohortSchema]**](CohortSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_cohort_schema import PaginatedResponseCohortSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseCohortSchema from a JSON string
paginated_response_cohort_schema_instance = PaginatedResponseCohortSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseCohortSchema.to_json()

# convert the object into a dict
paginated_response_cohort_schema_dict = paginated_response_cohort_schema_instance.to_dict()
# create an instance of PaginatedResponseCohortSchema from a dict
paginated_response_cohort_schema_from_dict = PaginatedResponseCohortSchema.from_dict(paginated_response_cohort_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


