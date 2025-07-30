# UpdateReportResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**ReportSchema2**](ReportSchema2.md) |  | 

## Example

```python
from haplohub.models.update_report_response import UpdateReportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateReportResponse from a JSON string
update_report_response_instance = UpdateReportResponse.from_json(json)
# print the JSON string representation of the object
print UpdateReportResponse.to_json()

# convert the object into a dict
update_report_response_dict = update_report_response_instance.to_dict()
# create an instance of UpdateReportResponse from a dict
update_report_response_from_dict = UpdateReportResponse.from_dict(update_report_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


