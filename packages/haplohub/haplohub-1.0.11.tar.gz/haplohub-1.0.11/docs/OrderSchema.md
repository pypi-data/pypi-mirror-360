# OrderSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**age** | **int** |  | [optional] 
**dob** | **date** |  | [optional] 
**clia_number** | **str** |  | [optional] 
**patient** | **str** |  | [optional] 
**provider** | **str** |  | [optional] 
**laboratory** | **str** |  | [optional] 
**date_reported** | **datetime** |  | [optional] 
**date_collected** | **datetime** |  | [optional] 
**specimen_number** | **str** |  | [optional] 
**date_received** | **datetime** |  | [optional] 
**status** | **str** |  | [optional] 
**interpretation** | **str** |  | [optional] 

## Example

```python
from haplohub.models.order_schema import OrderSchema

# TODO update the JSON string below
json = "{}"
# create an instance of OrderSchema from a JSON string
order_schema_instance = OrderSchema.from_json(json)
# print the JSON string representation of the object
print OrderSchema.to_json()

# convert the object into a dict
order_schema_dict = order_schema_instance.to_dict()
# create an instance of OrderSchema from a dict
order_schema_from_dict = OrderSchema.from_dict(order_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


