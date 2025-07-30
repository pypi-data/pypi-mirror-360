# UpdateCohortRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from haplohub.models.update_cohort_request import UpdateCohortRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCohortRequest from a JSON string
update_cohort_request_instance = UpdateCohortRequest.from_json(json)
# print the JSON string representation of the object
print UpdateCohortRequest.to_json()

# convert the object into a dict
update_cohort_request_dict = update_cohort_request_instance.to_dict()
# create an instance of UpdateCohortRequest from a dict
update_cohort_request_from_dict = UpdateCohortRequest.from_dict(update_cohort_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


