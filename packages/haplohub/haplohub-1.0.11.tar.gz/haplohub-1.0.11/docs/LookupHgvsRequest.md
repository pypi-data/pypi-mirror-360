# LookupHgvsRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sample_id** | **int** |  | 
**hgvs** | **List[str]** |  | 

## Example

```python
from haplohub.models.lookup_hgvs_request import LookupHgvsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LookupHgvsRequest from a JSON string
lookup_hgvs_request_instance = LookupHgvsRequest.from_json(json)
# print the JSON string representation of the object
print LookupHgvsRequest.to_json()

# convert the object into a dict
lookup_hgvs_request_dict = lookup_hgvs_request_instance.to_dict()
# create an instance of LookupHgvsRequest from a dict
lookup_hgvs_request_from_dict = LookupHgvsRequest.from_dict(lookup_hgvs_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


