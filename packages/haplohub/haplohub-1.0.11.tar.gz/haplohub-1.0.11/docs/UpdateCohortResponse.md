# UpdateCohortResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**CohortDetailSchema**](CohortDetailSchema.md) |  | 

## Example

```python
from haplohub.models.update_cohort_response import UpdateCohortResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCohortResponse from a JSON string
update_cohort_response_instance = UpdateCohortResponse.from_json(json)
# print the JSON string representation of the object
print UpdateCohortResponse.to_json()

# convert the object into a dict
update_cohort_response_dict = update_cohort_response_instance.to_dict()
# create an instance of UpdateCohortResponse from a dict
update_cohort_response_from_dict = UpdateCohortResponse.from_dict(update_cohort_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


