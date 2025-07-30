# DownloadLinkSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**download_link** | **str** |  | 
**file_name** | **str** |  | 
**file_size** | **int** |  | [optional] 

## Example

```python
from haplohub.models.download_link_schema import DownloadLinkSchema

# TODO update the JSON string below
json = "{}"
# create an instance of DownloadLinkSchema from a JSON string
download_link_schema_instance = DownloadLinkSchema.from_json(json)
# print the JSON string representation of the object
print DownloadLinkSchema.to_json()

# convert the object into a dict
download_link_schema_dict = download_link_schema_instance.to_dict()
# create an instance of DownloadLinkSchema from a dict
download_link_schema_from_dict = DownloadLinkSchema.from_dict(download_link_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


