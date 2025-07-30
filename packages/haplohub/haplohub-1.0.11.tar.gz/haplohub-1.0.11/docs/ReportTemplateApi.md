# haplohub.ReportTemplateApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_report_template**](ReportTemplateApi.md#create_report_template) | **POST** /api/v1/report-template/ | Create report template
[**delete_report_template**](ReportTemplateApi.md#delete_report_template) | **DELETE** /api/v1/report-template/{report_template_id}/ | Delete report template
[**get_report_template**](ReportTemplateApi.md#get_report_template) | **GET** /api/v1/report-template/{report_template_id}/ | Get report template
[**list_report_templates**](ReportTemplateApi.md#list_report_templates) | **GET** /api/v1/report-template/ | List report templates
[**preview_report_template**](ReportTemplateApi.md#preview_report_template) | **GET** /api/v1/report-template/{report_template_id}/preview/ | Preview report template
[**update_report_template**](ReportTemplateApi.md#update_report_template) | **PUT** /api/v1/report-template/{report_template_id}/ | Update report template


# **create_report_template**
> CreateReportTemplateResponse create_report_template(create_report_template_request)

Create report template

Create a new report template

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_report_template_request import CreateReportTemplateRequest
from haplohub.models.create_report_template_response import CreateReportTemplateResponse
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
    api_instance = haplohub.ReportTemplateApi(api_client)
    create_report_template_request = haplohub.CreateReportTemplateRequest() # CreateReportTemplateRequest | 

    try:
        # Create report template
        api_response = api_instance.create_report_template(create_report_template_request)
        print("The response of ReportTemplateApi->create_report_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportTemplateApi->create_report_template: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_report_template_request** | [**CreateReportTemplateRequest**](CreateReportTemplateRequest.md)|  | 

### Return type

[**CreateReportTemplateResponse**](CreateReportTemplateResponse.md)

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

# **delete_report_template**
> GenericResponse delete_report_template(report_template_id)

Delete report template

Delete report template by its ID

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
    api_instance = haplohub.ReportTemplateApi(api_client)
    report_template_id = 'report_template_id_example' # str | 

    try:
        # Delete report template
        api_response = api_instance.delete_report_template(report_template_id)
        print("The response of ReportTemplateApi->delete_report_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportTemplateApi->delete_report_template: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_template_id** | **str**|  | 

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

# **get_report_template**
> GetReportTemplateResponse get_report_template(report_template_id)

Get report template

Get report template by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_report_template_response import GetReportTemplateResponse
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
    api_instance = haplohub.ReportTemplateApi(api_client)
    report_template_id = 'report_template_id_example' # str | 

    try:
        # Get report template
        api_response = api_instance.get_report_template(report_template_id)
        print("The response of ReportTemplateApi->get_report_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportTemplateApi->get_report_template: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_template_id** | **str**|  | 

### Return type

[**GetReportTemplateResponse**](GetReportTemplateResponse.md)

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

# **list_report_templates**
> PaginatedResponseReportTemplateSchema list_report_templates()

List report templates

List all report templates

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_report_template_schema import PaginatedResponseReportTemplateSchema
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
    api_instance = haplohub.ReportTemplateApi(api_client)

    try:
        # List report templates
        api_response = api_instance.list_report_templates()
        print("The response of ReportTemplateApi->list_report_templates:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportTemplateApi->list_report_templates: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseReportTemplateSchema**](PaginatedResponseReportTemplateSchema.md)

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

# **preview_report_template**
> preview_report_template(report_template_id)

Preview report template

Preview report template by its ID

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
    api_instance = haplohub.ReportTemplateApi(api_client)
    report_template_id = 'report_template_id_example' # str | 

    try:
        # Preview report template
        api_instance.preview_report_template(report_template_id)
    except Exception as e:
        print("Exception when calling ReportTemplateApi->preview_report_template: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_template_id** | **str**|  | 

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

# **update_report_template**
> UpdateReportTemplateResponse update_report_template(report_template_id, update_report_template_request)

Update report template

Update report template by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.update_report_template_request import UpdateReportTemplateRequest
from haplohub.models.update_report_template_response import UpdateReportTemplateResponse
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
    api_instance = haplohub.ReportTemplateApi(api_client)
    report_template_id = 'report_template_id_example' # str | 
    update_report_template_request = haplohub.UpdateReportTemplateRequest() # UpdateReportTemplateRequest | 

    try:
        # Update report template
        api_response = api_instance.update_report_template(report_template_id, update_report_template_request)
        print("The response of ReportTemplateApi->update_report_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReportTemplateApi->update_report_template: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_template_id** | **str**|  | 
 **update_report_template_request** | [**UpdateReportTemplateRequest**](UpdateReportTemplateRequest.md)|  | 

### Return type

[**UpdateReportTemplateResponse**](UpdateReportTemplateResponse.md)

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

