# InfinityPaginatedResponseLogSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**items** | [**List[LogSchema]**](LogSchema.md) |  | 
**has_more** | **bool** |  | 
**cursor** | **str** |  | [optional] 

## Example

```python
from haplohub.models.infinity_paginated_response_log_schema import InfinityPaginatedResponseLogSchema

# TODO update the JSON string below
json = "{}"
# create an instance of InfinityPaginatedResponseLogSchema from a JSON string
infinity_paginated_response_log_schema_instance = InfinityPaginatedResponseLogSchema.from_json(json)
# print the JSON string representation of the object
print InfinityPaginatedResponseLogSchema.to_json()

# convert the object into a dict
infinity_paginated_response_log_schema_dict = infinity_paginated_response_log_schema_instance.to_dict()
# create an instance of InfinityPaginatedResponseLogSchema from a dict
infinity_paginated_response_log_schema_from_dict = InfinityPaginatedResponseLogSchema.from_dict(infinity_paginated_response_log_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


