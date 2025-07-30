# AccessionSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chromosome** | **str** |  | 
**accession** | **str** |  | 
**length** | **int** |  | 
**build** | **str** |  | 
**build_version** | **str** |  | 

## Example

```python
from haplohub.models.accession_schema import AccessionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of AccessionSchema from a JSON string
accession_schema_instance = AccessionSchema.from_json(json)
# print the JSON string representation of the object
print AccessionSchema.to_json()

# convert the object into a dict
accession_schema_dict = accession_schema_instance.to_dict()
# create an instance of AccessionSchema from a dict
accession_schema_from_dict = AccessionSchema.from_dict(accession_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


