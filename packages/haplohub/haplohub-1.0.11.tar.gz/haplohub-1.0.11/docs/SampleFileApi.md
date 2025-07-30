# haplohub.SampleFileApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_sample_file**](SampleFileApi.md#delete_sample_file) | **DELETE** /api/v1/cohort/{cohort_id}/sample-file/{sample_file_id}/ | Delete sample file
[**download_link**](SampleFileApi.md#download_link) | **POST** /api/v1/cohort/{cohort_id}/sample-file/{sample_file_id}/download-link/ | Get download link
[**finish_uploading**](SampleFileApi.md#finish_uploading) | **POST** /api/v1/cohort/{cohort_id}/sample-file/finish-uploading/ | Finish uploading
[**get_sample_file**](SampleFileApi.md#get_sample_file) | **GET** /api/v1/cohort/{cohort_id}/sample-file/{sample_file_id}/ | Get sample file
[**list_sample_files**](SampleFileApi.md#list_sample_files) | **GET** /api/v1/cohort/{cohort_id}/sample-file/ | List sample files


# **delete_sample_file**
> ResultResponse delete_sample_file(cohort_id, sample_file_id)

Delete sample file

Delete sample file by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response import ResultResponse
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
    api_instance = haplohub.SampleFileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    sample_file_id = 'sample_file_id_example' # str | 

    try:
        # Delete sample file
        api_response = api_instance.delete_sample_file(cohort_id, sample_file_id)
        print("The response of SampleFileApi->delete_sample_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleFileApi->delete_sample_file: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **sample_file_id** | **str**|  | 

### Return type

[**ResultResponse**](ResultResponse.md)

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

# **download_link**
> ResultResponseDownloadLinkSchema download_link(cohort_id, sample_file_id)

Get download link

Get download link by sample file ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_download_link_schema import ResultResponseDownloadLinkSchema
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
    api_instance = haplohub.SampleFileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    sample_file_id = 'sample_file_id_example' # str | 

    try:
        # Get download link
        api_response = api_instance.download_link(cohort_id, sample_file_id)
        print("The response of SampleFileApi->download_link:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleFileApi->download_link: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **sample_file_id** | **str**|  | 

### Return type

[**ResultResponseDownloadLinkSchema**](ResultResponseDownloadLinkSchema.md)

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

# **finish_uploading**
> ResultResponseSampleFileSchema finish_uploading(cohort_id, finish_uploading_request)

Finish uploading

Finish uploading a new sample file

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.finish_uploading_request import FinishUploadingRequest
from haplohub.models.result_response_sample_file_schema import ResultResponseSampleFileSchema
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
    api_instance = haplohub.SampleFileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    finish_uploading_request = haplohub.FinishUploadingRequest() # FinishUploadingRequest | 

    try:
        # Finish uploading
        api_response = api_instance.finish_uploading(cohort_id, finish_uploading_request)
        print("The response of SampleFileApi->finish_uploading:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleFileApi->finish_uploading: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **finish_uploading_request** | [**FinishUploadingRequest**](FinishUploadingRequest.md)|  | 

### Return type

[**ResultResponseSampleFileSchema**](ResultResponseSampleFileSchema.md)

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

# **get_sample_file**
> ResultResponseSampleFileSchema get_sample_file(cohort_id, sample_file_id)

Get sample file

Get sample file by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_sample_file_schema import ResultResponseSampleFileSchema
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
    api_instance = haplohub.SampleFileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    sample_file_id = 'sample_file_id_example' # str | 

    try:
        # Get sample file
        api_response = api_instance.get_sample_file(cohort_id, sample_file_id)
        print("The response of SampleFileApi->get_sample_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleFileApi->get_sample_file: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **sample_file_id** | **str**|  | 

### Return type

[**ResultResponseSampleFileSchema**](ResultResponseSampleFileSchema.md)

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

# **list_sample_files**
> PaginatedResponseSampleFileSchema list_sample_files(cohort_id)

List sample files

List all sample files

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_sample_file_schema import PaginatedResponseSampleFileSchema
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
    api_instance = haplohub.SampleFileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 

    try:
        # List sample files
        api_response = api_instance.list_sample_files(cohort_id)
        print("The response of SampleFileApi->list_sample_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleFileApi->list_sample_files: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 

### Return type

[**PaginatedResponseSampleFileSchema**](PaginatedResponseSampleFileSchema.md)

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

