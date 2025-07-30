# helloasso_python.CommandesApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**items_item_id_get**](CommandesApi.md#items_item_id_get) | **GET** /items/{itemId} | Obtenir le détail d&#39;un article contenu dans une commande
[**orders_order_id_cancel_post**](CommandesApi.md#orders_order_id_cancel_post) | **POST** /orders/{orderId}/cancel | Annuler les paiements futurs pour une commande (pas de remboursement).
[**orders_order_id_get**](CommandesApi.md#orders_order_id_get) | **GET** /orders/{orderId} | Obtenir des informations détaillées sur une commande
[**organizations_organization_slug_forms_form_type_form_slug_items_get**](CommandesApi.md#organizations_organization_slug_forms_form_type_form_slug_items_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/items | Obtenir une liste d&#39;articles vendus dans un formulaire
[**organizations_organization_slug_forms_form_type_form_slug_orders_get**](CommandesApi.md#organizations_organization_slug_forms_form_type_form_slug_orders_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/orders | Obtenir les commandes d&#39;un formulaire
[**organizations_organization_slug_items_get**](CommandesApi.md#organizations_organization_slug_items_get) | **GET** /organizations/{organizationSlug}/items | Obtenir une liste d&#39;articles vendus par une organisation
[**organizations_organization_slug_orders_get**](CommandesApi.md#organizations_organization_slug_orders_get) | **GET** /organizations/{organizationSlug}/orders | Obtenir les commandes d&#39;une organisation


# **items_item_id_get**
> HelloAssoApiV5ModelsStatisticsItemDetail items_item_id_get(item_id, with_details=with_details)

Obtenir le détail d'un article contenu dans une commande

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>FormAdmin<br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_statistics_item_detail import HelloAssoApiV5ModelsStatisticsItemDetail
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
    api_instance = helloasso_python.CommandesApi(api_client)
    item_id = 56 # int | The item ID
    with_details = False # bool | Set to true to return CustomFields and Options (optional) (default to False)

    try:
        # Obtenir le détail d'un article contenu dans une commande
        api_response = api_instance.items_item_id_get(item_id, with_details=with_details)
        print("The response of CommandesApi->items_item_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommandesApi->items_item_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **item_id** | **int**| The item ID | 
 **with_details** | **bool**| Set to true to return CustomFields and Options | [optional] [default to False]

### Return type

[**HelloAssoApiV5ModelsStatisticsItemDetail**](HelloAssoApiV5ModelsStatisticsItemDetail.md)

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

# **orders_order_id_cancel_post**
> orders_order_id_cancel_post(order_id)

Annuler les paiements futurs pour une commande (pas de remboursement).

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/>FormAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> RefundManagement<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
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
    api_instance = helloasso_python.CommandesApi(api_client)
    order_id = 56 # int | The order identifier.

    try:
        # Annuler les paiements futurs pour une commande (pas de remboursement).
        api_instance.orders_order_id_cancel_post(order_id)
    except Exception as e:
        print("Exception when calling CommandesApi->orders_order_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **int**| The order identifier. | 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **orders_order_id_get**
> HelloAssoApiV5ModelsStatisticsOrderDetail orders_order_id_get(order_id)

Obtenir des informations détaillées sur une commande

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>FormAdmin<br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_statistics_order_detail import HelloAssoApiV5ModelsStatisticsOrderDetail
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
    api_instance = helloasso_python.CommandesApi(api_client)
    order_id = 56 # int | 

    try:
        # Obtenir des informations détaillées sur une commande
        api_response = api_instance.orders_order_id_get(order_id)
        print("The response of CommandesApi->orders_order_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommandesApi->orders_order_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **int**|  | 

### Return type

[**HelloAssoApiV5ModelsStatisticsOrderDetail**](HelloAssoApiV5ModelsStatisticsOrderDetail.md)

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

# **organizations_organization_slug_forms_form_type_form_slug_items_get**
> organizations_organization_slug_forms_form_type_form_slug_items_get(organization_slug, form_slug, form_type, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, tier_types=tier_types, item_states=item_states, tier_name=tier_name, with_details=with_details, sort_order=sort_order, sort_field=sort_field, with_count=with_count)

Obtenir une liste d'articles vendus dans un formulaire

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>FormAdmin<br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.hello_asso_api_v5_models_enums_item_state import HelloAssoApiV5ModelsEnumsItemState
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_field import HelloAssoApiV5ModelsEnumsSortField
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_order import HelloAssoApiV5ModelsEnumsSortOrder
from helloasso_python.models.hello_asso_api_v5_models_enums_tier_type import HelloAssoApiV5ModelsEnumsTierType
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
    api_instance = helloasso_python.CommandesApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization slug
    form_slug = 'form_slug_example' # str | The form slug
    form_type = helloasso_python.HelloAssoApiV5ModelsEnumsFormType() # HelloAssoApiV5ModelsEnumsFormType | The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop
    var_from = '2013-10-20T19:20:30+01:00' # datetime | First Date Filter (optional)
    to = '2013-10-20T19:20:30+01:00' # datetime | End Date Filter (exclusive) (optional)
    user_search_key = 'user_search_key_example' # str | Filter results on user or payer first name, last name or email (optional)
    page_index = 1 # int | The page of results to retrieve (optional) (default to 1)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    tier_types = [helloasso_python.HelloAssoApiV5ModelsEnumsTierType()] # List[HelloAssoApiV5ModelsEnumsTierType] | The type of tiers (optional)
    item_states = [helloasso_python.HelloAssoApiV5ModelsEnumsItemState()] # List[HelloAssoApiV5ModelsEnumsItemState] | The item states  Available values: * `Processed` - The item is paid and is valid * `Registered` - The item has been registered manually by the organization and is valid * `Unknown` * `Canceled` - The item has been canceled, and is no longer valid (optional)
    tier_name = 'tier_name_example' # str | The name of a tier (optional)
    with_details = False # bool | Set to true to return CustomFields and Options (optional) (default to False)
    sort_order = helloasso_python.HelloAssoApiV5ModelsEnumsSortOrder() # HelloAssoApiV5ModelsEnumsSortOrder | Sort forms items by ascending or descending order. Default is descending (optional)
    sort_field = helloasso_python.HelloAssoApiV5ModelsEnumsSortField() # HelloAssoApiV5ModelsEnumsSortField | Sort forms items by a specific field (Date or UpdateDate). Default is date (optional)
    with_count = False # bool | Whether the pagination should include totalCount and totalPages. (optional) (default to False)

    try:
        # Obtenir une liste d'articles vendus dans un formulaire
        api_instance.organizations_organization_slug_forms_form_type_form_slug_items_get(organization_slug, form_slug, form_type, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, tier_types=tier_types, item_states=item_states, tier_name=tier_name, with_details=with_details, sort_order=sort_order, sort_field=sort_field, with_count=with_count)
    except Exception as e:
        print("Exception when calling CommandesApi->organizations_organization_slug_forms_form_type_form_slug_items_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization slug | 
 **form_slug** | **str**| The form slug | 
 **form_type** | [**HelloAssoApiV5ModelsEnumsFormType**](.md)| The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop | 
 **var_from** | **datetime**| First Date Filter | [optional] 
 **to** | **datetime**| End Date Filter (exclusive) | [optional] 
 **user_search_key** | **str**| Filter results on user or payer first name, last name or email | [optional] 
 **page_index** | **int**| The page of results to retrieve | [optional] [default to 1]
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **tier_types** | [**List[HelloAssoApiV5ModelsEnumsTierType]**](HelloAssoApiV5ModelsEnumsTierType.md)| The type of tiers | [optional] 
 **item_states** | [**List[HelloAssoApiV5ModelsEnumsItemState]**](HelloAssoApiV5ModelsEnumsItemState.md)| The item states  Available values: * &#x60;Processed&#x60; - The item is paid and is valid * &#x60;Registered&#x60; - The item has been registered manually by the organization and is valid * &#x60;Unknown&#x60; * &#x60;Canceled&#x60; - The item has been canceled, and is no longer valid | [optional] 
 **tier_name** | **str**| The name of a tier | [optional] 
 **with_details** | **bool**| Set to true to return CustomFields and Options | [optional] [default to False]
 **sort_order** | [**HelloAssoApiV5ModelsEnumsSortOrder**](.md)| Sort forms items by ascending or descending order. Default is descending | [optional] 
 **sort_field** | [**HelloAssoApiV5ModelsEnumsSortField**](.md)| Sort forms items by a specific field (Date or UpdateDate). Default is date | [optional] 
 **with_count** | **bool**| Whether the pagination should include totalCount and totalPages. | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **organizations_organization_slug_forms_form_type_form_slug_orders_get**
> ResultsWithPaginationModelOrder organizations_organization_slug_forms_form_type_form_slug_orders_get(organization_slug, form_slug, form_type, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, with_details=with_details, sort_order=sort_order, with_count=with_count)

Obtenir les commandes d'un formulaire

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>FormAdmin<br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_order import HelloAssoApiV5ModelsEnumsSortOrder
from helloasso_python.models.results_with_pagination_model_order import ResultsWithPaginationModelOrder
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
    api_instance = helloasso_python.CommandesApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization slug
    form_slug = 'form_slug_example' # str | The form slug
    form_type = helloasso_python.HelloAssoApiV5ModelsEnumsFormType() # HelloAssoApiV5ModelsEnumsFormType | The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop
    var_from = '2013-10-20T19:20:30+01:00' # datetime | First Date Filter (optional)
    to = '2013-10-20T19:20:30+01:00' # datetime | End Date Filter (exclusive) (optional)
    user_search_key = 'user_search_key_example' # str | Filter results on user or payer first name, last name or email (optional)
    page_index = 1 # int | The page of results to retrieve (optional) (default to 1)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    with_details = False # bool | Set to true to return CustomFields (optional) (default to False)
    sort_order = helloasso_python.HelloAssoApiV5ModelsEnumsSortOrder() # HelloAssoApiV5ModelsEnumsSortOrder | Sort forms orders by ascending or descending order. Default is descending (optional)
    with_count = False # bool | Whether the pagination should include totalCount and totalPages. (optional) (default to False)

    try:
        # Obtenir les commandes d'un formulaire
        api_response = api_instance.organizations_organization_slug_forms_form_type_form_slug_orders_get(organization_slug, form_slug, form_type, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, with_details=with_details, sort_order=sort_order, with_count=with_count)
        print("The response of CommandesApi->organizations_organization_slug_forms_form_type_form_slug_orders_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommandesApi->organizations_organization_slug_forms_form_type_form_slug_orders_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization slug | 
 **form_slug** | **str**| The form slug | 
 **form_type** | [**HelloAssoApiV5ModelsEnumsFormType**](.md)| The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop | 
 **var_from** | **datetime**| First Date Filter | [optional] 
 **to** | **datetime**| End Date Filter (exclusive) | [optional] 
 **user_search_key** | **str**| Filter results on user or payer first name, last name or email | [optional] 
 **page_index** | **int**| The page of results to retrieve | [optional] [default to 1]
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **with_details** | **bool**| Set to true to return CustomFields | [optional] [default to False]
 **sort_order** | [**HelloAssoApiV5ModelsEnumsSortOrder**](.md)| Sort forms orders by ascending or descending order. Default is descending | [optional] 
 **with_count** | **bool**| Whether the pagination should include totalCount and totalPages. | [optional] [default to False]

### Return type

[**ResultsWithPaginationModelOrder**](ResultsWithPaginationModelOrder.md)

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

# **organizations_organization_slug_items_get**
> organizations_organization_slug_items_get(organization_slug, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, tier_types=tier_types, item_states=item_states, tier_name=tier_name, with_details=with_details, sort_order=sort_order, sort_field=sort_field, with_count=with_count)

Obtenir une liste d'articles vendus par une organisation

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_item_state import HelloAssoApiV5ModelsEnumsItemState
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_field import HelloAssoApiV5ModelsEnumsSortField
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_order import HelloAssoApiV5ModelsEnumsSortOrder
from helloasso_python.models.hello_asso_api_v5_models_enums_tier_type import HelloAssoApiV5ModelsEnumsTierType
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
    api_instance = helloasso_python.CommandesApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization slug
    var_from = '2013-10-20T19:20:30+01:00' # datetime | First Date Filter (optional)
    to = '2013-10-20T19:20:30+01:00' # datetime | End Date Filter (exclusive) (optional)
    user_search_key = 'user_search_key_example' # str | Filter results on user or payer first name, last name or email (optional)
    page_index = 1 # int | The page of results to retrieve (optional) (default to 1)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    tier_types = [helloasso_python.HelloAssoApiV5ModelsEnumsTierType()] # List[HelloAssoApiV5ModelsEnumsTierType] | The type of tiers Donation, Payment, Registration, Membership, MonthlyDonation, MonthlyPayment, OfflineDonation, Contribution, Bonus (optional)
    item_states = [helloasso_python.HelloAssoApiV5ModelsEnumsItemState()] # List[HelloAssoApiV5ModelsEnumsItemState] | The item states  Available values: * `Processed` - The item is paid and is valid * `Registered` - The item has been registered manually by the organization and is valid * `Unknown` * `Canceled` - The item has been canceled, and is no longer valid (optional)
    tier_name = 'tier_name_example' # str | The name of a tier (optional)
    with_details = False # bool | Set to true to return CustomFields and Options (optional) (default to False)
    sort_order = helloasso_python.HelloAssoApiV5ModelsEnumsSortOrder() # HelloAssoApiV5ModelsEnumsSortOrder | Sort organizations items by ascending or descending order. Default is descending (optional)
    sort_field = helloasso_python.HelloAssoApiV5ModelsEnumsSortField() # HelloAssoApiV5ModelsEnumsSortField | Sort organizations items by a specific field (Date or UpdateDate). Default is date (optional)
    with_count = False # bool | Whether the pagination should include totalCount and totalPages. (optional) (default to False)

    try:
        # Obtenir une liste d'articles vendus par une organisation
        api_instance.organizations_organization_slug_items_get(organization_slug, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, tier_types=tier_types, item_states=item_states, tier_name=tier_name, with_details=with_details, sort_order=sort_order, sort_field=sort_field, with_count=with_count)
    except Exception as e:
        print("Exception when calling CommandesApi->organizations_organization_slug_items_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization slug | 
 **var_from** | **datetime**| First Date Filter | [optional] 
 **to** | **datetime**| End Date Filter (exclusive) | [optional] 
 **user_search_key** | **str**| Filter results on user or payer first name, last name or email | [optional] 
 **page_index** | **int**| The page of results to retrieve | [optional] [default to 1]
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **tier_types** | [**List[HelloAssoApiV5ModelsEnumsTierType]**](HelloAssoApiV5ModelsEnumsTierType.md)| The type of tiers Donation, Payment, Registration, Membership, MonthlyDonation, MonthlyPayment, OfflineDonation, Contribution, Bonus | [optional] 
 **item_states** | [**List[HelloAssoApiV5ModelsEnumsItemState]**](HelloAssoApiV5ModelsEnumsItemState.md)| The item states  Available values: * &#x60;Processed&#x60; - The item is paid and is valid * &#x60;Registered&#x60; - The item has been registered manually by the organization and is valid * &#x60;Unknown&#x60; * &#x60;Canceled&#x60; - The item has been canceled, and is no longer valid | [optional] 
 **tier_name** | **str**| The name of a tier | [optional] 
 **with_details** | **bool**| Set to true to return CustomFields and Options | [optional] [default to False]
 **sort_order** | [**HelloAssoApiV5ModelsEnumsSortOrder**](.md)| Sort organizations items by ascending or descending order. Default is descending | [optional] 
 **sort_field** | [**HelloAssoApiV5ModelsEnumsSortField**](.md)| Sort organizations items by a specific field (Date or UpdateDate). Default is date | [optional] 
 **with_count** | **bool**| Whether the pagination should include totalCount and totalPages. | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **organizations_organization_slug_orders_get**
> ResultsWithPaginationModelOrder organizations_organization_slug_orders_get(organization_slug, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, form_types=form_types, with_details=with_details, sort_order=sort_order, with_count=with_count)

Obtenir les commandes d'une organisation

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_order import HelloAssoApiV5ModelsEnumsSortOrder
from helloasso_python.models.results_with_pagination_model_order import ResultsWithPaginationModelOrder
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
    api_instance = helloasso_python.CommandesApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization slug
    var_from = '2013-10-20T19:20:30+01:00' # datetime | First Date Filter (optional)
    to = '2013-10-20T19:20:30+01:00' # datetime | End Date Filter (exclusive) (optional)
    user_search_key = 'user_search_key_example' # str | Filter results on user or payer first name, last name or email (optional)
    page_index = 1 # int | The page of results to retrieve (optional) (default to 1)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    form_types = [helloasso_python.HelloAssoApiV5ModelsEnumsFormType()] # List[HelloAssoApiV5ModelsEnumsFormType] | The type of the form CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop (optional)
    with_details = False # bool | Set to true to return CustomFields (optional) (default to False)
    sort_order = helloasso_python.HelloAssoApiV5ModelsEnumsSortOrder() # HelloAssoApiV5ModelsEnumsSortOrder | Sort organizations orders by ascending or descending order. Default is descending (optional)
    with_count = False # bool | Whether the pagination should include totalCount and totalPages. (optional) (default to False)

    try:
        # Obtenir les commandes d'une organisation
        api_response = api_instance.organizations_organization_slug_orders_get(organization_slug, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, form_types=form_types, with_details=with_details, sort_order=sort_order, with_count=with_count)
        print("The response of CommandesApi->organizations_organization_slug_orders_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommandesApi->organizations_organization_slug_orders_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization slug | 
 **var_from** | **datetime**| First Date Filter | [optional] 
 **to** | **datetime**| End Date Filter (exclusive) | [optional] 
 **user_search_key** | **str**| Filter results on user or payer first name, last name or email | [optional] 
 **page_index** | **int**| The page of results to retrieve | [optional] [default to 1]
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **form_types** | [**List[HelloAssoApiV5ModelsEnumsFormType]**](HelloAssoApiV5ModelsEnumsFormType.md)| The type of the form CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop | [optional] 
 **with_details** | **bool**| Set to true to return CustomFields | [optional] [default to False]
 **sort_order** | [**HelloAssoApiV5ModelsEnumsSortOrder**](.md)| Sort organizations orders by ascending or descending order. Default is descending | [optional] 
 **with_count** | **bool**| Whether the pagination should include totalCount and totalPages. | [optional] [default to False]

### Return type

[**ResultsWithPaginationModelOrder**](ResultsWithPaginationModelOrder.md)

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

