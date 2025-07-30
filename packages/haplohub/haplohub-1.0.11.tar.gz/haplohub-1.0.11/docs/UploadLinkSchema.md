# UploadLinkSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upload_link** | **str** |  | 
**upload_request** | [**UploadRequstSchema**](UploadRequstSchema.md) |  | 

## Example

```python
from haplohub.models.upload_link_schema import UploadLinkSchema

# TODO update the JSON string below
json = "{}"
# create an instance of UploadLinkSchema from a JSON string
upload_link_schema_instance = UploadLinkSchema.from_json(json)
# print the JSON string representation of the object
print UploadLinkSchema.to_json()

# convert the object into a dict
upload_link_schema_dict = upload_link_schema_instance.to_dict()
# create an instance of UploadLinkSchema from a dict
upload_link_schema_from_dict = UploadLinkSchema.from_dict(upload_link_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


