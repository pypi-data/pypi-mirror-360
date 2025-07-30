# PaginatedResponseReportSchema2


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[ReportSchema2]**](ReportSchema2.md) |  | 

## Example

```python
from haplohub.models.paginated_response_report_schema2 import PaginatedResponseReportSchema2

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseReportSchema2 from a JSON string
paginated_response_report_schema2_instance = PaginatedResponseReportSchema2.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseReportSchema2.to_json()

# convert the object into a dict
paginated_response_report_schema2_dict = paginated_response_report_schema2_instance.to_dict()
# create an instance of PaginatedResponseReportSchema2 from a dict
paginated_response_report_schema2_from_dict = PaginatedResponseReportSchema2.from_dict(paginated_response_report_schema2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


