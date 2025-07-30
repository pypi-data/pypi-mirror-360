# ResultResponseDownloadLinkSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**DownloadLinkSchema**](DownloadLinkSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_download_link_schema import ResultResponseDownloadLinkSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseDownloadLinkSchema from a JSON string
result_response_download_link_schema_instance = ResultResponseDownloadLinkSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseDownloadLinkSchema.to_json()

# convert the object into a dict
result_response_download_link_schema_dict = result_response_download_link_schema_instance.to_dict()
# create an instance of ResultResponseDownloadLinkSchema from a dict
result_response_download_link_schema_from_dict = ResultResponseDownloadLinkSchema.from_dict(result_response_download_link_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


