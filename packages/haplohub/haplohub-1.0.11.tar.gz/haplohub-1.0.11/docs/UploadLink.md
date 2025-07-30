# UploadLink


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**original_file_path** | **str** |  | 
**file_path** | **str** |  | 
**signed_url** | **str** |  | 

## Example

```python
from haplohub.models.upload_link import UploadLink

# TODO update the JSON string below
json = "{}"
# create an instance of UploadLink from a JSON string
upload_link_instance = UploadLink.from_json(json)
# print the JSON string representation of the object
print UploadLink.to_json()

# convert the object into a dict
upload_link_dict = upload_link_instance.to_dict()
# create an instance of UploadLink from a dict
upload_link_from_dict = UploadLink.from_dict(upload_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


