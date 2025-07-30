# ReportTemplateSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | 
**description** | **str** |  | [optional] [default to '']
**report_type** | **str** |  | [optional] [default to 'text']
**template** | **str** |  | [optional] [default to '']
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.report_template_schema import ReportTemplateSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ReportTemplateSchema from a JSON string
report_template_schema_instance = ReportTemplateSchema.from_json(json)
# print the JSON string representation of the object
print ReportTemplateSchema.to_json()

# convert the object into a dict
report_template_schema_dict = report_template_schema_instance.to_dict()
# create an instance of ReportTemplateSchema from a dict
report_template_schema_from_dict = ReportTemplateSchema.from_dict(report_template_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


