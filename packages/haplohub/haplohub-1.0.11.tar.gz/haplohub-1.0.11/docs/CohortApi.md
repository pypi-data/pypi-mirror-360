# haplohub.CohortApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_cohort**](CohortApi.md#create_cohort) | **POST** /api/v1/cohort/ | Create cohort
[**delete_cohort**](CohortApi.md#delete_cohort) | **DELETE** /api/v1/cohort/{cohort_id}/ | Delete cohort
[**get_cohort**](CohortApi.md#get_cohort) | **GET** /api/v1/cohort/{cohort_id}/ | Get cohort
[**list_cohorts**](CohortApi.md#list_cohorts) | **GET** /api/v1/cohort/ | List cohorts
[**update_cohort**](CohortApi.md#update_cohort) | **PUT** /api/v1/cohort/{cohort_id}/ | Update cohort


# **create_cohort**
> CreateCohortResponse create_cohort(create_cohort_request)

Create cohort

Create a new cohort

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_cohort_request import CreateCohortRequest
from haplohub.models.create_cohort_response import CreateCohortResponse
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
    api_instance = haplohub.CohortApi(api_client)
    create_cohort_request = haplohub.CreateCohortRequest() # CreateCohortRequest | 

    try:
        # Create cohort
        api_response = api_instance.create_cohort(create_cohort_request)
        print("The response of CohortApi->create_cohort:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CohortApi->create_cohort: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_cohort_request** | [**CreateCohortRequest**](CreateCohortRequest.md)|  | 

### Return type

[**CreateCohortResponse**](CreateCohortResponse.md)

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

# **delete_cohort**
> GenericResponse delete_cohort(cohort_id)

Delete cohort

Delete cohort by its ID

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
    api_instance = haplohub.CohortApi(api_client)
    cohort_id = 'cohort_id_example' # str | 

    try:
        # Delete cohort
        api_response = api_instance.delete_cohort(cohort_id)
        print("The response of CohortApi->delete_cohort:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CohortApi->delete_cohort: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 

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

# **get_cohort**
> GetCohortResponse get_cohort(cohort_id)

Get cohort

Get cohort by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_cohort_response import GetCohortResponse
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
    api_instance = haplohub.CohortApi(api_client)
    cohort_id = 'cohort_id_example' # str | 

    try:
        # Get cohort
        api_response = api_instance.get_cohort(cohort_id)
        print("The response of CohortApi->get_cohort:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CohortApi->get_cohort: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 

### Return type

[**GetCohortResponse**](GetCohortResponse.md)

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

# **list_cohorts**
> PaginatedResponseCohortSchema list_cohorts()

List cohorts

List all cohorts

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_cohort_schema import PaginatedResponseCohortSchema
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
    api_instance = haplohub.CohortApi(api_client)

    try:
        # List cohorts
        api_response = api_instance.list_cohorts()
        print("The response of CohortApi->list_cohorts:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CohortApi->list_cohorts: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseCohortSchema**](PaginatedResponseCohortSchema.md)

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

# **update_cohort**
> UpdateCohortResponse update_cohort(cohort_id, update_cohort_request)

Update cohort

Update cohort by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.update_cohort_request import UpdateCohortRequest
from haplohub.models.update_cohort_response import UpdateCohortResponse
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
    api_instance = haplohub.CohortApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    update_cohort_request = haplohub.UpdateCohortRequest() # UpdateCohortRequest | 

    try:
        # Update cohort
        api_response = api_instance.update_cohort(cohort_id, update_cohort_request)
        print("The response of CohortApi->update_cohort:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CohortApi->update_cohort: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **update_cohort_request** | [**UpdateCohortRequest**](UpdateCohortRequest.md)|  | 

### Return type

[**UpdateCohortResponse**](UpdateCohortResponse.md)

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

