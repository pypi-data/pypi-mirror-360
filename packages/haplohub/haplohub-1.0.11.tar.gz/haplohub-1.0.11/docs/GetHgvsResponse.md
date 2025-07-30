# GetHgvsResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**HgvsDosageSchema**](HgvsDosageSchema.md) |  | 

## Example

```python
from haplohub.models.get_hgvs_response import GetHgvsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetHgvsResponse from a JSON string
get_hgvs_response_instance = GetHgvsResponse.from_json(json)
# print the JSON string representation of the object
print GetHgvsResponse.to_json()

# convert the object into a dict
get_hgvs_response_dict = get_hgvs_response_instance.to_dict()
# create an instance of GetHgvsResponse from a dict
get_hgvs_response_from_dict = GetHgvsResponse.from_dict(get_hgvs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


