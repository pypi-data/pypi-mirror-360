# CreateCohortRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | 

## Example

```python
from haplohub.models.create_cohort_request import CreateCohortRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCohortRequest from a JSON string
create_cohort_request_instance = CreateCohortRequest.from_json(json)
# print the JSON string representation of the object
print CreateCohortRequest.to_json()

# convert the object into a dict
create_cohort_request_dict = create_cohort_request_instance.to_dict()
# create an instance of CreateCohortRequest from a dict
create_cohort_request_from_dict = CreateCohortRequest.from_dict(create_cohort_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


