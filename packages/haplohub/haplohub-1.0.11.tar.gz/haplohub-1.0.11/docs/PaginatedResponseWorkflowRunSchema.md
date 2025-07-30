# PaginatedResponseWorkflowRunSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[WorkflowRunSchema]**](WorkflowRunSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_workflow_run_schema import PaginatedResponseWorkflowRunSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseWorkflowRunSchema from a JSON string
paginated_response_workflow_run_schema_instance = PaginatedResponseWorkflowRunSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseWorkflowRunSchema.to_json()

# convert the object into a dict
paginated_response_workflow_run_schema_dict = paginated_response_workflow_run_schema_instance.to_dict()
# create an instance of PaginatedResponseWorkflowRunSchema from a dict
paginated_response_workflow_run_schema_from_dict = PaginatedResponseWorkflowRunSchema.from_dict(paginated_response_workflow_run_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


