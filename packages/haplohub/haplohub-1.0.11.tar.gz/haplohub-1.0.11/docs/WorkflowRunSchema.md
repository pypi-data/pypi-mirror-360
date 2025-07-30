# WorkflowRunSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**triggered_by** | [**UserSchema**](UserSchema.md) |  | [optional] 
**id** | **int** |  | [optional] 
**workflow_id** | **str** |  | 
**workflow_type** | **str** |  | 
**started_at** | **datetime** |  | 

## Example

```python
from haplohub.models.workflow_run_schema import WorkflowRunSchema

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowRunSchema from a JSON string
workflow_run_schema_instance = WorkflowRunSchema.from_json(json)
# print the JSON string representation of the object
print WorkflowRunSchema.to_json()

# convert the object into a dict
workflow_run_schema_dict = workflow_run_schema_instance.to_dict()
# create an instance of WorkflowRunSchema from a dict
workflow_run_schema_from_dict = WorkflowRunSchema.from_dict(workflow_run_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


