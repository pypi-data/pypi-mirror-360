# WorkflowHistorySchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | 
**note** | **str** |  | [optional] [default to '']
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.workflow_history_schema import WorkflowHistorySchema

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowHistorySchema from a JSON string
workflow_history_schema_instance = WorkflowHistorySchema.from_json(json)
# print the JSON string representation of the object
print WorkflowHistorySchema.to_json()

# convert the object into a dict
workflow_history_schema_dict = workflow_history_schema_instance.to_dict()
# create an instance of WorkflowHistorySchema from a dict
workflow_history_schema_from_dict = WorkflowHistorySchema.from_dict(workflow_history_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


