# haplohub.LogApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_logs**](LogApi.md#list_logs) | **GET** /api/v1/log/ | List logs


# **list_logs**
> InfinityPaginatedResponseLogSchema list_logs(page_size=page_size, cursor=cursor)

List logs

List all logs

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.infinity_paginated_response_log_schema import InfinityPaginatedResponseLogSchema
from haplohub.rest import ApiException
from pprint import pprint

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: 
configuration = haplohub.Configuration(
    access_token=os.environ["API_KEY"]
)

# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = haplohub.LogApi(api_client)
    page_size = 100 # int |  (optional) (default to 100)
    cursor = 'cursor_example' # str |  (optional)

    try:
        # List logs
        api_response = api_instance.list_logs(page_size=page_size, cursor=cursor)
        print("The response of LogApi->list_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LogApi->list_logs: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | [optional] [default to 100]
 **cursor** | **str**|  | [optional] 

### Return type

[**InfinityPaginatedResponseLogSchema**](InfinityPaginatedResponseLogSchema.md)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

