# CreateCohortResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**CohortSchema**](CohortSchema.md) |  | 

## Example

```python
from haplohub.models.create_cohort_response import CreateCohortResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCohortResponse from a JSON string
create_cohort_response_instance = CreateCohortResponse.from_json(json)
# print the JSON string representation of the object
print CreateCohortResponse.to_json()

# convert the object into a dict
create_cohort_response_dict = create_cohort_response_instance.to_dict()
# create an instance of CreateCohortResponse from a dict
create_cohort_response_from_dict = CreateCohortResponse.from_dict(create_cohort_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


