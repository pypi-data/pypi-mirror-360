# CreateReportTemplateResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**ReportTemplateSchema**](ReportTemplateSchema.md) |  | 

## Example

```python
from haplohub.models.create_report_template_response import CreateReportTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReportTemplateResponse from a JSON string
create_report_template_response_instance = CreateReportTemplateResponse.from_json(json)
# print the JSON string representation of the object
print CreateReportTemplateResponse.to_json()

# convert the object into a dict
create_report_template_response_dict = create_report_template_response_instance.to_dict()
# create an instance of CreateReportTemplateResponse from a dict
create_report_template_response_from_dict = CreateReportTemplateResponse.from_dict(create_report_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


