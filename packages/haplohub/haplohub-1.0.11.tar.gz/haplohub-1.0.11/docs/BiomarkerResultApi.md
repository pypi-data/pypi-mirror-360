# haplohub.BiomarkerResultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_biomarker_results**](BiomarkerResultApi.md#list_biomarker_results) | **GET** /api/v1/cohort/{cohort_id}/biomarker_result/ | List biomarker results


# **list_biomarker_results**
> ResultListResponseBiomarkerResultSchema list_biomarker_results(cohort_id, order_id=order_id)

List biomarker results

List all biomarker results

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_list_response_biomarker_result_schema import ResultListResponseBiomarkerResultSchema
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
    api_instance = haplohub.BiomarkerResultApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    order_id = 'order_id_example' # str |  (optional)

    try:
        # List biomarker results
        api_response = api_instance.list_biomarker_results(cohort_id, order_id=order_id)
        print("The response of BiomarkerResultApi->list_biomarker_results:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BiomarkerResultApi->list_biomarker_results: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **order_id** | **str**|  | [optional] 

### Return type

[**ResultListResponseBiomarkerResultSchema**](ResultListResponseBiomarkerResultSchema.md)

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

