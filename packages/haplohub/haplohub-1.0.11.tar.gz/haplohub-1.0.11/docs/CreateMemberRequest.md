# CreateMemberRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**patient_id** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**gender** | **str** |  | [optional] 
**birth_date** | **str** |  | [optional] 

## Example

```python
from haplohub.models.create_member_request import CreateMemberRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateMemberRequest from a JSON string
create_member_request_instance = CreateMemberRequest.from_json(json)
# print the JSON string representation of the object
print CreateMemberRequest.to_json()

# convert the object into a dict
create_member_request_dict = create_member_request_instance.to_dict()
# create an instance of CreateMemberRequest from a dict
create_member_request_from_dict = CreateMemberRequest.from_dict(create_member_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


