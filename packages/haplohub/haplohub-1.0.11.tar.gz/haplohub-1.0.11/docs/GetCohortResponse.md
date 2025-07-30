# GetCohortResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**CohortDetailSchema**](CohortDetailSchema.md) |  | 

## Example

```python
from haplohub.models.get_cohort_response import GetCohortResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCohortResponse from a JSON string
get_cohort_response_instance = GetCohortResponse.from_json(json)
# print the JSON string representation of the object
print GetCohortResponse.to_json()

# convert the object into a dict
get_cohort_response_dict = get_cohort_response_instance.to_dict()
# create an instance of GetCohortResponse from a dict
get_cohort_response_from_dict = GetCohortResponse.from_dict(get_cohort_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


