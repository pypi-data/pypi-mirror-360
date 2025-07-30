# PaginatedResponseMemberSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[MemberSchema]**](MemberSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_member_schema import PaginatedResponseMemberSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseMemberSchema from a JSON string
paginated_response_member_schema_instance = PaginatedResponseMemberSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseMemberSchema.to_json()

# convert the object into a dict
paginated_response_member_schema_dict = paginated_response_member_schema_instance.to_dict()
# create an instance of PaginatedResponseMemberSchema from a dict
paginated_response_member_schema_from_dict = PaginatedResponseMemberSchema.from_dict(paginated_response_member_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


