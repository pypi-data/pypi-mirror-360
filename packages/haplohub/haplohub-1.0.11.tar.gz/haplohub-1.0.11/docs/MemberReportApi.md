# haplohub.MemberReportApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_member_report**](MemberReportApi.md#create_member_report) | **POST** /api/v1/cohort/{cohort_id}/member/{member_id}/report/{report_template_id}/create/ | Create member report


# **create_member_report**
> bytearray create_member_report(cohort_id, member_id, report_template_id)

Create member report

Create member report by its ID

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
    api_instance = haplohub.MemberReportApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    member_id = 'member_id_example' # str | 
    report_template_id = 'report_template_id_example' # str | 

    try:
        # Create member report
        api_response = api_instance.create_member_report(cohort_id, member_id, report_template_id)
        print("The response of MemberReportApi->create_member_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberReportApi->create_member_report: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **member_id** | **str**|  | 
 **report_template_id** | **str**|  | 

### Return type

**bytearray**

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/pdf

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

