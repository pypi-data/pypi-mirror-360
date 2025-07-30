# ResponseSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status_code** | **int** |  | 

## Example

```python
from haplohub.models.response_schema import ResponseSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResponseSchema from a JSON string
response_schema_instance = ResponseSchema.from_json(json)
# print the JSON string representation of the object
print ResponseSchema.to_json()

# convert the object into a dict
response_schema_dict = response_schema_instance.to_dict()
# create an instance of ResponseSchema from a dict
response_schema_from_dict = ResponseSchema.from_dict(response_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


