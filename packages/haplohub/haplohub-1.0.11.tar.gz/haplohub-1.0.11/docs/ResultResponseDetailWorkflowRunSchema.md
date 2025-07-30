# ResultResponseDetailWorkflowRunSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**DetailWorkflowRunSchema**](DetailWorkflowRunSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_detail_workflow_run_schema import ResultResponseDetailWorkflowRunSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseDetailWorkflowRunSchema from a JSON string
result_response_detail_workflow_run_schema_instance = ResultResponseDetailWorkflowRunSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseDetailWorkflowRunSchema.to_json()

# convert the object into a dict
result_response_detail_workflow_run_schema_dict = result_response_detail_workflow_run_schema_instance.to_dict()
# create an instance of ResultResponseDetailWorkflowRunSchema from a dict
result_response_detail_workflow_run_schema_from_dict = ResultResponseDetailWorkflowRunSchema.from_dict(result_response_detail_workflow_run_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


