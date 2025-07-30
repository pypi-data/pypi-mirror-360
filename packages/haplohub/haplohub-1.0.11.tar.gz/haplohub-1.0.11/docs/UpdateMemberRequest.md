# UpdateMemberRequest


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
from haplohub.models.update_member_request import UpdateMemberRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateMemberRequest from a JSON string
update_member_request_instance = UpdateMemberRequest.from_json(json)
# print the JSON string representation of the object
print UpdateMemberRequest.to_json()

# convert the object into a dict
update_member_request_dict = update_member_request_instance.to_dict()
# create an instance of UpdateMemberRequest from a dict
update_member_request_from_dict = UpdateMemberRequest.from_dict(update_member_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


