# haplohub.ApiKeyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**haplohub_api_v1_api_key_create_api_key**](ApiKeyApi.md#haplohub_api_v1_api_key_create_api_key) | **POST** /api/v1/api-key/ | Create Api Key
[**haplohub_api_v1_api_key_delete_api_key**](ApiKeyApi.md#haplohub_api_v1_api_key_delete_api_key) | **DELETE** /api/v1/api-key/{api_key_id}/ | Delete Api Key
[**haplohub_api_v1_api_key_list_api_keys**](ApiKeyApi.md#haplohub_api_v1_api_key_list_api_keys) | **GET** /api/v1/api-key/ | List Api Keys


# **haplohub_api_v1_api_key_create_api_key**
> ResultResponseApiKeySchema haplohub_api_v1_api_key_create_api_key(create_api_key_schema)

Create Api Key

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_api_key_schema import CreateApiKeySchema
from haplohub.models.result_response_api_key_schema import ResultResponseApiKeySchema
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
    api_instance = haplohub.ApiKeyApi(api_client)
    create_api_key_schema = haplohub.CreateApiKeySchema() # CreateApiKeySchema | 

    try:
        # Create Api Key
        api_response = api_instance.haplohub_api_v1_api_key_create_api_key(create_api_key_schema)
        print("The response of ApiKeyApi->haplohub_api_v1_api_key_create_api_key:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApiKeyApi->haplohub_api_v1_api_key_create_api_key: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_api_key_schema** | [**CreateApiKeySchema**](CreateApiKeySchema.md)|  | 

### Return type

[**ResultResponseApiKeySchema**](ResultResponseApiKeySchema.md)

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

# **haplohub_api_v1_api_key_delete_api_key**
> GenericResponse haplohub_api_v1_api_key_delete_api_key(api_key_id)

Delete Api Key

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.generic_response import GenericResponse
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
    api_instance = haplohub.ApiKeyApi(api_client)
    api_key_id = 'api_key_id_example' # str | 

    try:
        # Delete Api Key
        api_response = api_instance.haplohub_api_v1_api_key_delete_api_key(api_key_id)
        print("The response of ApiKeyApi->haplohub_api_v1_api_key_delete_api_key:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApiKeyApi->haplohub_api_v1_api_key_delete_api_key: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key_id** | **str**|  | 

### Return type

[**GenericResponse**](GenericResponse.md)

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

# **haplohub_api_v1_api_key_list_api_keys**
> PaginatedResponseApiKeySchema haplohub_api_v1_api_key_list_api_keys()

List Api Keys

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_api_key_schema import PaginatedResponseApiKeySchema
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
    api_instance = haplohub.ApiKeyApi(api_client)

    try:
        # List Api Keys
        api_response = api_instance.haplohub_api_v1_api_key_list_api_keys()
        print("The response of ApiKeyApi->haplohub_api_v1_api_key_list_api_keys:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApiKeyApi->haplohub_api_v1_api_key_list_api_keys: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseApiKeySchema**](PaginatedResponseApiKeySchema.md)

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

