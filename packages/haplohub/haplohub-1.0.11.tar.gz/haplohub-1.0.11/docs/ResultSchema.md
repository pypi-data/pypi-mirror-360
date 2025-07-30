# ResultSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**slug** | **str** |  | 
**value** | **float** |  | [optional] 
**result** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**unit** | **str** |  | [optional] 
**timestamp** | **datetime** |  | [optional] 
**notes** | **str** |  | [optional] 
**min_range_value** | **float** |  | [optional] 
**max_range_value** | **float** |  | [optional] 
**is_above_max_range** | **bool** |  | [optional] 
**is_below_min_range** | **bool** |  | [optional] 
**interpretation** | **str** |  | [optional] 
**loinc** | **str** |  | [optional] 
**loinc_slug** | **str** |  | [optional] 
**provider_id** | **str** |  | [optional] 

## Example

```python
from haplohub.models.result_schema import ResultSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultSchema from a JSON string
result_schema_instance = ResultSchema.from_json(json)
# print the JSON string representation of the object
print ResultSchema.to_json()

# convert the object into a dict
result_schema_dict = result_schema_instance.to_dict()
# create an instance of ResultSchema from a dict
result_schema_from_dict = ResultSchema.from_dict(result_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


