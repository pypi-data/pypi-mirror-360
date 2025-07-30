# CreateReportTemplateRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**report_type** | [**ReportType**](ReportType.md) |  | 

## Example

```python
from haplohub.models.create_report_template_request import CreateReportTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReportTemplateRequest from a JSON string
create_report_template_request_instance = CreateReportTemplateRequest.from_json(json)
# print the JSON string representation of the object
print CreateReportTemplateRequest.to_json()

# convert the object into a dict
create_report_template_request_dict = create_report_template_request_instance.to_dict()
# create an instance of CreateReportTemplateRequest from a dict
create_report_template_request_from_dict = CreateReportTemplateRequest.from_dict(create_report_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


