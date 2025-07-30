# helloasso_python.TagsApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**tags_tag_name_get**](TagsApi.md#tags_tag_name_get) | **GET** /tags/{tagName} | Obtenir le détail d&#39;un tag interne


# **tags_tag_name_get**
> HelloAssoApiV5ModelsTagsInternalTagModel tags_tag_name_get(tag_name, with_count=with_count, with_amount=with_amount)

Obtenir le détail d'un tag interne

<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> FormOpenDirectory<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_tags_internal_tag_model import HelloAssoApiV5ModelsTagsInternalTagModel
from helloasso_python.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.helloasso.com/v5
# See configuration.py for a list of all supported configuration parameters.
configuration = helloasso_python.Configuration(
    host = "https://api.helloasso.com/v5"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with helloasso_python.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = helloasso_python.TagsApi(api_client)
    tag_name = 'tag_name_example' # str | 
    with_count = False # bool | If true : Count of times Tag is used (optional) (default to False)
    with_amount = False # bool | If true : Amount collected by all forms linked to this Tag (optional) (default to False)

    try:
        # Obtenir le détail d'un tag interne
        api_response = api_instance.tags_tag_name_get(tag_name, with_count=with_count, with_amount=with_amount)
        print("The response of TagsApi->tags_tag_name_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TagsApi->tags_tag_name_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tag_name** | **str**|  | 
 **with_count** | **bool**| If true : Count of times Tag is used | [optional] [default to False]
 **with_amount** | **bool**| If true : Amount collected by all forms linked to this Tag | [optional] [default to False]

### Return type

[**HelloAssoApiV5ModelsTagsInternalTagModel**](HelloAssoApiV5ModelsTagsInternalTagModel.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

