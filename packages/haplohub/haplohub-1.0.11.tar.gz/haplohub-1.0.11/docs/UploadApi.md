# haplohub.UploadApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_upload_request**](UploadApi.md#create_upload_request) | **POST** /api/v1/cohort/{cohort_id}/upload/request/ | Create upload request


# **create_upload_request**
> Response create_upload_request(cohort_id, create_upload_request_request)

Create upload request

Create a new upload request

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_upload_request_request import CreateUploadRequestRequest
from haplohub.models.response import Response
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
    api_instance = haplohub.UploadApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    create_upload_request_request = haplohub.CreateUploadRequestRequest() # CreateUploadRequestRequest | 

    try:
        # Create upload request
        api_response = api_instance.create_upload_request(cohort_id, create_upload_request_request)
        print("The response of UploadApi->create_upload_request:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadApi->create_upload_request: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **create_upload_request_request** | [**CreateUploadRequestRequest**](CreateUploadRequestRequest.md)|  | 

### Return type

[**Response**](Response.md)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

