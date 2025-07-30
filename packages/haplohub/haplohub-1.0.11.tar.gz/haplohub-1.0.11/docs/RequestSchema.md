# RequestSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**method** | **str** |  | 
**path** | **str** |  | 
**env_id** | **int** |  | 

## Example

```python
from haplohub.models.request_schema import RequestSchema

# TODO update the JSON string below
json = "{}"
# create an instance of RequestSchema from a JSON string
request_schema_instance = RequestSchema.from_json(json)
# print the JSON string representation of the object
print RequestSchema.to_json()

# convert the object into a dict
request_schema_dict = request_schema_instance.to_dict()
# create an instance of RequestSchema from a dict
request_schema_from_dict = RequestSchema.from_dict(request_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


