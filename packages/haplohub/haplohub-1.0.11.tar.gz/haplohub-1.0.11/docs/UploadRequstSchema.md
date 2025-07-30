# UploadRequstSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**filename** | **str** |  | 
**file_size** | **int** |  | 
**md5_checksum** | **str** |  | 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.upload_requst_schema import UploadRequstSchema

# TODO update the JSON string below
json = "{}"
# create an instance of UploadRequstSchema from a JSON string
upload_requst_schema_instance = UploadRequstSchema.from_json(json)
# print the JSON string representation of the object
print UploadRequstSchema.to_json()

# convert the object into a dict
upload_requst_schema_dict = upload_requst_schema_instance.to_dict()
# create an instance of UploadRequstSchema from a dict
upload_requst_schema_from_dict = UploadRequstSchema.from_dict(upload_requst_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


