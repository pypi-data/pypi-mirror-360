# CreateReportResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**ReportSchema2**](ReportSchema2.md) |  | 

## Example

```python
from haplohub.models.create_report_response import CreateReportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReportResponse from a JSON string
create_report_response_instance = CreateReportResponse.from_json(json)
# print the JSON string representation of the object
print CreateReportResponse.to_json()

# convert the object into a dict
create_report_response_dict = create_report_response_instance.to_dict()
# create an instance of CreateReportResponse from a dict
create_report_response_from_dict = CreateReportResponse.from_dict(create_report_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


