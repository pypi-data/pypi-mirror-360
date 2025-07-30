# haplohub.WorkflowApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_workflow_run**](WorkflowApi.md#get_workflow_run) | **GET** /api/v1/workflow/run/{workflow_run_id}/ | Get workflow run
[**list_workflow_runs**](WorkflowApi.md#list_workflow_runs) | **GET** /api/v1/workflow/run/ | List workflow runs


# **get_workflow_run**
> ResultResponseDetailWorkflowRunSchema get_workflow_run(workflow_run_id)

Get workflow run

Get workflow run by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_detail_workflow_run_schema import ResultResponseDetailWorkflowRunSchema
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
    api_instance = haplohub.WorkflowApi(api_client)
    workflow_run_id = 'workflow_run_id_example' # str | 

    try:
        # Get workflow run
        api_response = api_instance.get_workflow_run(workflow_run_id)
        print("The response of WorkflowApi->get_workflow_run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowApi->get_workflow_run: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_run_id** | **str**|  | 

### Return type

[**ResultResponseDetailWorkflowRunSchema**](ResultResponseDetailWorkflowRunSchema.md)

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

# **list_workflow_runs**
> PaginatedResponseWorkflowRunSchema list_workflow_runs()

List workflow runs

List all workflow runs

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_workflow_run_schema import PaginatedResponseWorkflowRunSchema
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
    api_instance = haplohub.WorkflowApi(api_client)

    try:
        # List workflow runs
        api_response = api_instance.list_workflow_runs()
        print("The response of WorkflowApi->list_workflow_runs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowApi->list_workflow_runs: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseWorkflowRunSchema**](PaginatedResponseWorkflowRunSchema.md)

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

