# haplohub.ReportApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_report**](ReportApi.md#create_report) | **POST** /api/v1/report/ | Create report
[**delete_report**](ReportApi.md#delete_report) | **DELETE** /api/v1/report/{report_id}/ | Delete report
[**get_report**](ReportApi.md#get_report) | **GET** /api/v1/report/{report_id}/ | Get report
[**list_reports**](ReportApi.md#list_reports) | **GET** /api/v1/report/ | List reports
[**preview_report**](ReportApi.md#preview_report) | **GET** /api/v1/report/{report_id}/preview/ | Preview report
[**update_report**](ReportApi.md#update_report) | **PUT** /api/v1/report/{report_id}/ | Update report


# **create_report**
> CreateReportResponse create_report(create_report_request)

Create report

Create a new report

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_report_request import CreateReportRequest
from haplohub.models.create_report_response import CreateReportResponse
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
    api_instance = haplohub.ReportApi(api_client)
    create_report_request = haplohub.CreateReportRequest() # CreateReportRequest | 

    try:
        # Create report
        api_response = api_instance.create_report(create_report_request)
        print("The response of ReportApi->create_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportApi->create_report: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_report_request** | [**CreateReportRequest**](CreateReportRequest.md)|  | 

### Return type

[**CreateReportResponse**](CreateReportResponse.md)

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

# **delete_report**
> GenericResponse delete_report(report_id)

Delete report

Delete report by its ID

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
    api_instance = haplohub.ReportApi(api_client)
    report_id = 'report_id_example' # str | 

    try:
        # Delete report
        api_response = api_instance.delete_report(report_id)
        print("The response of ReportApi->delete_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportApi->delete_report: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_id** | **str**|  | 

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

# **get_report**
> GetReportResponse get_report(report_id)

Get report

Get report by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_report_response import GetReportResponse
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
    api_instance = haplohub.ReportApi(api_client)
    report_id = 'report_id_example' # str | 

    try:
        # Get report
        api_response = api_instance.get_report(report_id)
        print("The response of ReportApi->get_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportApi->get_report: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_id** | **str**|  | 

### Return type

[**GetReportResponse**](GetReportResponse.md)

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

# **list_reports**
> PaginatedResponseReportSchema2 list_reports()

List reports

List all reports

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_report_schema2 import PaginatedResponseReportSchema2
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
    api_instance = haplohub.ReportApi(api_client)

    try:
        # List reports
        api_response = api_instance.list_reports()
        print("The response of ReportApi->list_reports:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportApi->list_reports: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseReportSchema2**](PaginatedResponseReportSchema2.md)

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

# **preview_report**
> preview_report(report_id)

Preview report

Preview report by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
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
    api_instance = haplohub.ReportApi(api_client)
    report_id = 'report_id_example' # str | 

    try:
        # Preview report
        api_instance.preview_report(report_id)
    except Exception as e:
        print("Exception when calling ReportApi->preview_report: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_report**
> UpdateReportResponse update_report(report_id, update_report_request)

Update report

Update report by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.update_report_request import UpdateReportRequest
from haplohub.models.update_report_response import UpdateReportResponse
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
    api_instance = haplohub.ReportApi(api_client)
    report_id = 'report_id_example' # str | 
    update_report_request = haplohub.UpdateReportRequest() # UpdateReportRequest | 

    try:
        # Update report
        api_response = api_instance.update_report(report_id, update_report_request)
        print("The response of ReportApi->update_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportApi->update_report: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_id** | **str**|  | 
 **update_report_request** | [**UpdateReportRequest**](UpdateReportRequest.md)|  | 

### Return type

[**UpdateReportResponse**](UpdateReportResponse.md)

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

