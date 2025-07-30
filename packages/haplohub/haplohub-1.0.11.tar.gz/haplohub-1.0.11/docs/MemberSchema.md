# MemberSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**patient_id** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**gender** | **str** |  | [optional] 
**birth_date** | **date** |  | [optional] 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.member_schema import MemberSchema

# TODO update the JSON string below
json = "{}"
# create an instance of MemberSchema from a JSON string
member_schema_instance = MemberSchema.from_json(json)
# print the JSON string representation of the object
print MemberSchema.to_json()

# convert the object into a dict
member_schema_dict = member_schema_instance.to_dict()
# create an instance of MemberSchema from a dict
member_schema_from_dict = MemberSchema.from_dict(member_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


