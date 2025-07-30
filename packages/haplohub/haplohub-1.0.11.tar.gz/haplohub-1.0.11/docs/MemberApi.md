# haplohub.MemberApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_member**](MemberApi.md#create_member) | **POST** /api/v1/cohort/{cohort_id}/member/ | Create member
[**delete_member**](MemberApi.md#delete_member) | **DELETE** /api/v1/cohort/{cohort_id}/member/{member_id}/ | Delete member
[**get_member**](MemberApi.md#get_member) | **GET** /api/v1/cohort/{cohort_id}/member/{member_id}/ | Get member
[**list_members**](MemberApi.md#list_members) | **GET** /api/v1/cohort/{cohort_id}/member/ | List members
[**update_member**](MemberApi.md#update_member) | **PUT** /api/v1/cohort/{cohort_id}/member/{member_id}/ | Update member


# **create_member**
> ResultResponseMemberSchema create_member(cohort_id, create_member_request)

Create member

Create a new member

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_member_request import CreateMemberRequest
from haplohub.models.result_response_member_schema import ResultResponseMemberSchema
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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    create_member_request = haplohub.CreateMemberRequest() # CreateMemberRequest | 

    try:
        # Create member
        api_response = api_instance.create_member(cohort_id, create_member_request)
        print("The response of MemberApi->create_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->create_member: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **create_member_request** | [**CreateMemberRequest**](CreateMemberRequest.md)|  | 

### Return type

[**ResultResponseMemberSchema**](ResultResponseMemberSchema.md)

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

# **delete_member**
> SuccessResponse delete_member(cohort_id, member_id)

Delete member

Delete member by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.success_response import SuccessResponse
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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    member_id = 'member_id_example' # str | 

    try:
        # Delete member
        api_response = api_instance.delete_member(cohort_id, member_id)
        print("The response of MemberApi->delete_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->delete_member: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **member_id** | **str**|  | 

### Return type

[**SuccessResponse**](SuccessResponse.md)

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

# **get_member**
> ResultResponseMemberSchema get_member(cohort_id, member_id)

Get member

Get member by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_member_schema import ResultResponseMemberSchema
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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    member_id = 'member_id_example' # str | 

    try:
        # Get member
        api_response = api_instance.get_member(cohort_id, member_id)
        print("The response of MemberApi->get_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->get_member: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **member_id** | **str**|  | 

### Return type

[**ResultResponseMemberSchema**](ResultResponseMemberSchema.md)

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

# **list_members**
> PaginatedResponseMemberSchema list_members(cohort_id)

List members

List all members

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_member_schema import PaginatedResponseMemberSchema
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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 

    try:
        # List members
        api_response = api_instance.list_members(cohort_id)
        print("The response of MemberApi->list_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->list_members: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 

### Return type

[**PaginatedResponseMemberSchema**](PaginatedResponseMemberSchema.md)

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

# **update_member**
> ResultResponseMemberSchema update_member(cohort_id, member_id, update_member_request)

Update member

Update member by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_member_schema import ResultResponseMemberSchema
from haplohub.models.update_member_request import UpdateMemberRequest
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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    member_id = 'member_id_example' # str | 
    update_member_request = haplohub.UpdateMemberRequest() # UpdateMemberRequest | 

    try:
        # Update member
        api_response = api_instance.update_member(cohort_id, member_id, update_member_request)
        print("The response of MemberApi->update_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->update_member: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **member_id** | **str**|  | 
 **update_member_request** | [**UpdateMemberRequest**](UpdateMemberRequest.md)|  | 

### Return type

[**ResultResponseMemberSchema**](ResultResponseMemberSchema.md)

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

