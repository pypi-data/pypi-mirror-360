# UpdateReportTemplateRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**report_type** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**template** | **str** |  | [optional] 

## Example

```python
from haplohub.models.update_report_template_request import UpdateReportTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateReportTemplateRequest from a JSON string
update_report_template_request_instance = UpdateReportTemplateRequest.from_json(json)
# print the JSON string representation of the object
print UpdateReportTemplateRequest.to_json()

# convert the object into a dict
update_report_template_request_dict = update_report_template_request_instance.to_dict()
# create an instance of UpdateReportTemplateRequest from a dict
update_report_template_request_from_dict = UpdateReportTemplateRequest.from_dict(update_report_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


