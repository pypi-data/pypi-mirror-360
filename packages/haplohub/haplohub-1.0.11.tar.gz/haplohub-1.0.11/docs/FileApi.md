# haplohub.FileApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_file**](FileApi.md#delete_file) | **DELETE** /api/v1/cohort/{cohort_id}/file/{file_id}/ | Delete file
[**download_link**](FileApi.md#download_link) | **POST** /api/v1/cohort/{cohort_id}/file/{file_id}/download-link/ | Get download link
[**download_link_by_path**](FileApi.md#download_link_by_path) | **POST** /api/v1/cohort/{cohort_id}/file/download-link/ | Get download link by file path
[**get_file**](FileApi.md#get_file) | **GET** /api/v1/cohort/{cohort_id}/file/{file_id}/ | Get file
[**list_files**](FileApi.md#list_files) | **GET** /api/v1/cohort/{cohort_id}/file/ | List files


# **delete_file**
> ResultResponse delete_file(cohort_id, file_id)

Delete file

Delete file by its ID

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
    api_instance = haplohub.FileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    file_id = 'file_id_example' # str | 

    try:
        # Delete file
        api_response = api_instance.delete_file(cohort_id, file_id)
        print("The response of FileApi->delete_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileApi->delete_file: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **file_id** | **str**|  | 

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
> ResultResponseDownloadLinkSchema download_link(cohort_id, file_id)

Get download link

Get download link by file ID

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
    api_instance = haplohub.FileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    file_id = 'file_id_example' # str | 

    try:
        # Get download link
        api_response = api_instance.download_link(cohort_id, file_id)
        print("The response of FileApi->download_link:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileApi->download_link: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **file_id** | **str**|  | 

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

# **download_link_by_path**
> ResultResponseDownloadLinkSchema download_link_by_path(cohort_id, path)

Get download link by file path

Get download link by file path

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
    api_instance = haplohub.FileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    path = 'path_example' # str | 

    try:
        # Get download link by file path
        api_response = api_instance.download_link_by_path(cohort_id, path)
        print("The response of FileApi->download_link_by_path:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileApi->download_link_by_path: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **path** | **str**|  | 

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

# **get_file**
> ResultResponseFileSchema get_file(cohort_id, file_id)

Get file

Get file by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_file_schema import ResultResponseFileSchema
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
    api_instance = haplohub.FileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    file_id = 'file_id_example' # str | 

    try:
        # Get file
        api_response = api_instance.get_file(cohort_id, file_id)
        print("The response of FileApi->get_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileApi->get_file: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **file_id** | **str**|  | 

### Return type

[**ResultResponseFileSchema**](ResultResponseFileSchema.md)

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

# **list_files**
> ResultResponseFileDirSchema list_files(cohort_id, recursive=recursive, sample_id=sample_id, member_id=member_id, path=path)

List files

List all files

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_file_dir_schema import ResultResponseFileDirSchema
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
    api_instance = haplohub.FileApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    recursive = True # bool |  (optional) (default to True)
    sample_id = 'sample_id_example' # str |  (optional)
    member_id = 'member_id_example' # str |  (optional)
    path = 'path_example' # str |  (optional)

    try:
        # List files
        api_response = api_instance.list_files(cohort_id, recursive=recursive, sample_id=sample_id, member_id=member_id, path=path)
        print("The response of FileApi->list_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileApi->list_files: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **recursive** | **bool**|  | [optional] [default to True]
 **sample_id** | **str**|  | [optional] 
 **member_id** | **str**|  | [optional] 
 **path** | **str**|  | [optional] 

### Return type

[**ResultResponseFileDirSchema**](ResultResponseFileDirSchema.md)

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

