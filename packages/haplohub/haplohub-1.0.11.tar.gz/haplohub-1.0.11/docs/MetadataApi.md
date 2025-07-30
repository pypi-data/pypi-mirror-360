# haplohub.MetadataApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_accession**](MetadataApi.md#list_accession) | **GET** /api/v1/metadata/accession/ | List Accessions


# **list_accession**
> PaginatedResponseAccessionSchema list_accession()

List Accessions

Genetic variants are typically defined as a difference from a reference. Each accession is a contiguous reference string. There is one accession per chromosome.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_accession_schema import PaginatedResponseAccessionSchema
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
    api_instance = haplohub.MetadataApi(api_client)

    try:
        # List Accessions
        api_response = api_instance.list_accession()
        print("The response of MetadataApi->list_accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->list_accession: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseAccessionSchema**](PaginatedResponseAccessionSchema.md)

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

