# GetReportTemplateResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**ReportTemplateSchema**](ReportTemplateSchema.md) |  | 

## Example

```python
from haplohub.models.get_report_template_response import GetReportTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetReportTemplateResponse from a JSON string
get_report_template_response_instance = GetReportTemplateResponse.from_json(json)
# print the JSON string representation of the object
print GetReportTemplateResponse.to_json()

# convert the object into a dict
get_report_template_response_dict = get_report_template_response_instance.to_dict()
# create an instance of GetReportTemplateResponse from a dict
get_report_template_response_from_dict = GetReportTemplateResponse.from_dict(get_report_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


