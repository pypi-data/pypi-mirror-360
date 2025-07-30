# UpdateReportTemplateResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**ReportTemplateSchema**](ReportTemplateSchema.md) |  | 

## Example

```python
from haplohub.models.update_report_template_response import UpdateReportTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateReportTemplateResponse from a JSON string
update_report_template_response_instance = UpdateReportTemplateResponse.from_json(json)
# print the JSON string representation of the object
print UpdateReportTemplateResponse.to_json()

# convert the object into a dict
update_report_template_response_dict = update_report_template_response_instance.to_dict()
# create an instance of UpdateReportTemplateResponse from a dict
update_report_template_response_from_dict = UpdateReportTemplateResponse.from_dict(update_report_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


