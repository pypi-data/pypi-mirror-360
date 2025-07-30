# ResultResponseMemberSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**MemberSchema**](MemberSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_member_schema import ResultResponseMemberSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseMemberSchema from a JSON string
result_response_member_schema_instance = ResultResponseMemberSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseMemberSchema.to_json()

# convert the object into a dict
result_response_member_schema_dict = result_response_member_schema_instance.to_dict()
# create an instance of ResultResponseMemberSchema from a dict
result_response_member_schema_from_dict = ResultResponseMemberSchema.from_dict(result_response_member_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


