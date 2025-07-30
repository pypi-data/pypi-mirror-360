# haplohub.PredictionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_prediction**](PredictionApi.md#get_prediction) | **GET** /api/v1/prediction/{prediction_id}/ | Get prediction
[**get_prediction_results**](PredictionApi.md#get_prediction_results) | **GET** /api/v1/prediction/{prediction_id}/results/ | Get prediction results
[**list_predictions**](PredictionApi.md#list_predictions) | **GET** /api/v1/prediction/ | List predictions
[**run_prediction**](PredictionApi.md#run_prediction) | **POST** /api/v1/prediction/ | Run prediction


# **get_prediction**
> GetPredictionResponse get_prediction(prediction_id)

Get prediction

Get prediction by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_prediction_response import GetPredictionResponse
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
    api_instance = haplohub.PredictionApi(api_client)
    prediction_id = 'prediction_id_example' # str | 

    try:
        # Get prediction
        api_response = api_instance.get_prediction(prediction_id)
        print("The response of PredictionApi->get_prediction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PredictionApi->get_prediction: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prediction_id** | **str**|  | 

### Return type

[**GetPredictionResponse**](GetPredictionResponse.md)

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

# **get_prediction_results**
> GetPredictionResultsResponse get_prediction_results(prediction_id)

Get prediction results

Get prediction results by prediction ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_prediction_results_response import GetPredictionResultsResponse
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
    api_instance = haplohub.PredictionApi(api_client)
    prediction_id = 'prediction_id_example' # str | 

    try:
        # Get prediction results
        api_response = api_instance.get_prediction_results(prediction_id)
        print("The response of PredictionApi->get_prediction_results:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PredictionApi->get_prediction_results: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prediction_id** | **str**|  | 

### Return type

[**GetPredictionResultsResponse**](GetPredictionResultsResponse.md)

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

# **list_predictions**
> PaginatedResponsePredictionSchema list_predictions()

List predictions

List all predictions

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_prediction_schema import PaginatedResponsePredictionSchema
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
    api_instance = haplohub.PredictionApi(api_client)

    try:
        # List predictions
        api_response = api_instance.list_predictions()
        print("The response of PredictionApi->list_predictions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PredictionApi->list_predictions: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponsePredictionSchema**](PaginatedResponsePredictionSchema.md)

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

# **run_prediction**
> RunPredictionResponse run_prediction(run_prediction_request)

Run prediction

Run a new prediction by specified version and model ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.run_prediction_request import RunPredictionRequest
from haplohub.models.run_prediction_response import RunPredictionResponse
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
    api_instance = haplohub.PredictionApi(api_client)
    run_prediction_request = haplohub.RunPredictionRequest() # RunPredictionRequest | 

    try:
        # Run prediction
        api_response = api_instance.run_prediction(run_prediction_request)
        print("The response of PredictionApi->run_prediction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PredictionApi->run_prediction: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_prediction_request** | [**RunPredictionRequest**](RunPredictionRequest.md)|  | 

### Return type

[**RunPredictionResponse**](RunPredictionResponse.md)

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

