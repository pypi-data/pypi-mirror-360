# helloasso_python.CheckoutApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**organizations_organization_slug_checkout_intents_checkout_intent_id_get**](CheckoutApi.md#organizations_organization_slug_checkout_intents_checkout_intent_id_get) | **GET** /organizations/{organizationSlug}/checkout-intents/{checkoutIntentId} | Récupérer une intention de paiement
[**organizations_organization_slug_checkout_intents_post**](CheckoutApi.md#organizations_organization_slug_checkout_intents_post) | **POST** /organizations/{organizationSlug}/checkout-intents | Initialisation d&#39;un Checkout


# **organizations_organization_slug_checkout_intents_checkout_intent_id_get**
> HelloAssoApiV5ModelsCartsCheckoutIntentResponse organizations_organization_slug_checkout_intents_checkout_intent_id_get(organization_slug, checkout_intent_id, with_failed_refund_operation=with_failed_refund_operation)

Récupérer une intention de paiement

Retourne aussi la commande associée. Uniquement dans le cas ou le paiement est autorisé.<br/><br/><b>Votre clientId doit avoir ces autorisations : </b> <br/> Checkout<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_carts_checkout_intent_response import HelloAssoApiV5ModelsCartsCheckoutIntentResponse
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
    api_instance = helloasso_python.CheckoutApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    checkout_intent_id = 56 # int | 
    with_failed_refund_operation = False # bool |  (optional) (default to False)

    try:
        # Récupérer une intention de paiement
        api_response = api_instance.organizations_organization_slug_checkout_intents_checkout_intent_id_get(organization_slug, checkout_intent_id, with_failed_refund_operation=with_failed_refund_operation)
        print("The response of CheckoutApi->organizations_organization_slug_checkout_intents_checkout_intent_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CheckoutApi->organizations_organization_slug_checkout_intents_checkout_intent_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **checkout_intent_id** | **int**|  | 
 **with_failed_refund_operation** | **bool**|  | [optional] [default to False]

### Return type

[**HelloAssoApiV5ModelsCartsCheckoutIntentResponse**](HelloAssoApiV5ModelsCartsCheckoutIntentResponse.md)

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

# **organizations_organization_slug_checkout_intents_post**
> HelloAssoApiV5ModelsCartsInitCheckoutResponse organizations_organization_slug_checkout_intents_post(organization_slug, hello_asso_api_v5_models_carts_init_checkout_body=hello_asso_api_v5_models_carts_init_checkout_body)

Initialisation d'un Checkout

Pour tout savoir sur Checkout consultez d'abord notre <a href="https://dev.helloasso.com/docs/description">documentation</a><br/><br/><b>Votre clientId doit avoir ces autorisations : </b> <br/> Checkout<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_carts_init_checkout_body import HelloAssoApiV5ModelsCartsInitCheckoutBody
from helloasso_python.models.hello_asso_api_v5_models_carts_init_checkout_response import HelloAssoApiV5ModelsCartsInitCheckoutResponse
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
    api_instance = helloasso_python.CheckoutApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    hello_asso_api_v5_models_carts_init_checkout_body = helloasso_python.HelloAssoApiV5ModelsCartsInitCheckoutBody() # HelloAssoApiV5ModelsCartsInitCheckoutBody |  (optional)

    try:
        # Initialisation d'un Checkout
        api_response = api_instance.organizations_organization_slug_checkout_intents_post(organization_slug, hello_asso_api_v5_models_carts_init_checkout_body=hello_asso_api_v5_models_carts_init_checkout_body)
        print("The response of CheckoutApi->organizations_organization_slug_checkout_intents_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CheckoutApi->organizations_organization_slug_checkout_intents_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **hello_asso_api_v5_models_carts_init_checkout_body** | [**HelloAssoApiV5ModelsCartsInitCheckoutBody**](HelloAssoApiV5ModelsCartsInitCheckoutBody.md)|  | [optional] 

### Return type

[**HelloAssoApiV5ModelsCartsInitCheckoutResponse**](HelloAssoApiV5ModelsCartsInitCheckoutResponse.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

