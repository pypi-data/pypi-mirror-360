# PaginatedResponseReportTemplateSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[ReportTemplateSchema]**](ReportTemplateSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_report_template_schema import PaginatedResponseReportTemplateSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseReportTemplateSchema from a JSON string
paginated_response_report_template_schema_instance = PaginatedResponseReportTemplateSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseReportTemplateSchema.to_json()

# convert the object into a dict
paginated_response_report_template_schema_dict = paginated_response_report_template_schema_instance.to_dict()
# create an instance of PaginatedResponseReportTemplateSchema from a dict
paginated_response_report_template_schema_from_dict = PaginatedResponseReportTemplateSchema.from_dict(paginated_response_report_template_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


