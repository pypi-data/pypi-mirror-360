# DetailWorkflowRunSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**triggered_by** | [**UserSchema**](UserSchema.md) |  | [optional] 
**id** | **int** |  | [optional] 
**workflow_id** | **str** |  | 
**workflow_type** | **str** |  | 
**started_at** | **datetime** |  | 
**extra** | **object** |  | 
**history** | [**List[WorkflowHistorySchema]**](WorkflowHistorySchema.md) |  | 

## Example

```python
from haplohub.models.detail_workflow_run_schema import DetailWorkflowRunSchema

# TODO update the JSON string below
json = "{}"
# create an instance of DetailWorkflowRunSchema from a JSON string
detail_workflow_run_schema_instance = DetailWorkflowRunSchema.from_json(json)
# print the JSON string representation of the object
print DetailWorkflowRunSchema.to_json()

# convert the object into a dict
detail_workflow_run_schema_dict = detail_workflow_run_schema_instance.to_dict()
# create an instance of DetailWorkflowRunSchema from a dict
detail_workflow_run_schema_from_dict = DetailWorkflowRunSchema.from_dict(detail_workflow_run_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


