# haplohub.EnvironmentsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_environment**](EnvironmentsApi.md#create_environment) | **POST** /api/v1/environments/ | Create environment
[**list_environments**](EnvironmentsApi.md#list_environments) | **GET** /api/v1/environments/ | List environments
[**switch_environment**](EnvironmentsApi.md#switch_environment) | **POST** /api/v1/environments/{environment_id}/switch/ | Switch environment


# **create_environment**
> CreateEnvironmentResponse create_environment(create_environment_request)

Create environment

Create a new environment

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_environment_request import CreateEnvironmentRequest
from haplohub.models.create_environment_response import CreateEnvironmentResponse
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
    api_instance = haplohub.EnvironmentsApi(api_client)
    create_environment_request = haplohub.CreateEnvironmentRequest() # CreateEnvironmentRequest | 

    try:
        # Create environment
        api_response = api_instance.create_environment(create_environment_request)
        print("The response of EnvironmentsApi->create_environment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnvironmentsApi->create_environment: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_environment_request** | [**CreateEnvironmentRequest**](CreateEnvironmentRequest.md)|  | 

### Return type

[**CreateEnvironmentResponse**](CreateEnvironmentResponse.md)

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

# **list_environments**
> PaginatedResponseEnvironmentSchema list_environments()

List environments

List all environments

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_environment_schema import PaginatedResponseEnvironmentSchema
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
    api_instance = haplohub.EnvironmentsApi(api_client)

    try:
        # List environments
        api_response = api_instance.list_environments()
        print("The response of EnvironmentsApi->list_environments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnvironmentsApi->list_environments: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseEnvironmentSchema**](PaginatedResponseEnvironmentSchema.md)

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

# **switch_environment**
> SwitchEnvironmentResponse switch_environment(environment_id)

Switch environment

Switch to an environment

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.switch_environment_response import SwitchEnvironmentResponse
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
    api_instance = haplohub.EnvironmentsApi(api_client)
    environment_id = 56 # int | 

    try:
        # Switch environment
        api_response = api_instance.switch_environment(environment_id)
        print("The response of EnvironmentsApi->switch_environment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnvironmentsApi->switch_environment: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **environment_id** | **int**|  | 

### Return type

[**SwitchEnvironmentResponse**](SwitchEnvironmentResponse.md)

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

