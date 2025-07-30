# ReportSchema2


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | 
**description** | **str** |  | [optional] [default to '']
**template** | **str** |  | [optional] [default to '']
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.report_schema2 import ReportSchema2

# TODO update the JSON string below
json = "{}"
# create an instance of ReportSchema2 from a JSON string
report_schema2_instance = ReportSchema2.from_json(json)
# print the JSON string representation of the object
print ReportSchema2.to_json()

# convert the object into a dict
report_schema2_dict = report_schema2_instance.to_dict()
# create an instance of ReportSchema2 from a dict
report_schema2_from_dict = ReportSchema2.from_dict(report_schema2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


