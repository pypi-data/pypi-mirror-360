# haplohub.ModelApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_model**](ModelApi.md#create_model) | **POST** /api/v1/model/ | Create model
[**list_models**](ModelApi.md#list_models) | **GET** /api/v1/model/ | List models
[**push_model**](ModelApi.md#push_model) | **POST** /api/v1/model/{model_id}/push/ | Push model


# **create_model**
> CreateModelResponse create_model(create_model_request)

Create model

Create a new model

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_model_request import CreateModelRequest
from haplohub.models.create_model_response import CreateModelResponse
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
    api_instance = haplohub.ModelApi(api_client)
    create_model_request = haplohub.CreateModelRequest() # CreateModelRequest | 

    try:
        # Create model
        api_response = api_instance.create_model(create_model_request)
        print("The response of ModelApi->create_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelApi->create_model: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_model_request** | [**CreateModelRequest**](CreateModelRequest.md)|  | 

### Return type

[**CreateModelResponse**](CreateModelResponse.md)

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

# **list_models**
> PaginatedResponseMLModelSchema list_models(name)

List models

List all models

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_ml_model_schema import PaginatedResponseMLModelSchema
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
    api_instance = haplohub.ModelApi(api_client)
    name = 'name_example' # str | 

    try:
        # List models
        api_response = api_instance.list_models(name)
        print("The response of ModelApi->list_models:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelApi->list_models: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**PaginatedResponseMLModelSchema**](PaginatedResponseMLModelSchema.md)

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

# **push_model**
> ResultResponsePushCredentials push_model(model_id, push_model_request)

Push model

Push a model to GCP

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.push_model_request import PushModelRequest
from haplohub.models.result_response_push_credentials import ResultResponsePushCredentials
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
    api_instance = haplohub.ModelApi(api_client)
    model_id = haplohub.ModelId() # ModelId | 
    push_model_request = haplohub.PushModelRequest() # PushModelRequest | 

    try:
        # Push model
        api_response = api_instance.push_model(model_id, push_model_request)
        print("The response of ModelApi->push_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelApi->push_model: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | [**ModelId**](.md)|  | 
 **push_model_request** | [**PushModelRequest**](PushModelRequest.md)|  | 

### Return type

[**ResultResponsePushCredentials**](ResultResponsePushCredentials.md)

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

