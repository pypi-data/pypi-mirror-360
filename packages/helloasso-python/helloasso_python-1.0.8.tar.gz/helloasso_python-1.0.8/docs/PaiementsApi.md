# helloasso_python.PaiementsApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**organizations_organization_slug_forms_form_type_form_slug_payments_get**](PaiementsApi.md#organizations_organization_slug_forms_form_type_form_slug_payments_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/payments | Obtenir les informations des paiements effectués sur un formulaire
[**organizations_organization_slug_payments_get**](PaiementsApi.md#organizations_organization_slug_payments_get) | **GET** /organizations/{organizationSlug}/payments | Obtenir les informations des paiements effectués sur une organisation
[**organizations_organization_slug_payments_search_get**](PaiementsApi.md#organizations_organization_slug_payments_search_get) | **GET** /organizations/{organizationSlug}/payments/search | Rechercher des paiements.
[**payments_payment_id_get**](PaiementsApi.md#payments_payment_id_get) | **GET** /payments/{paymentId} | Obtenir les informations détaillées d&#39;un paiement.
[**payments_payment_id_refund_post**](PaiementsApi.md#payments_payment_id_refund_post) | **POST** /payments/{paymentId}/refund | Rembourser un paiement.


# **organizations_organization_slug_forms_form_type_form_slug_payments_get**
> ResultsWithPaginationModelPayment organizations_organization_slug_forms_form_type_form_slug_payments_get(organization_slug, form_slug, form_type, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, states=states, sort_order=sort_order, sort_field=sort_field, with_count=with_count)

Obtenir les informations des paiements effectués sur un formulaire

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>FormAdmin<br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.hello_asso_api_v5_models_enums_payment_state import HelloAssoApiV5ModelsEnumsPaymentState
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_field import HelloAssoApiV5ModelsEnumsSortField
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_order import HelloAssoApiV5ModelsEnumsSortOrder
from helloasso_python.models.results_with_pagination_model_payment import ResultsWithPaginationModelPayment
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
    api_instance = helloasso_python.PaiementsApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization slug
    form_slug = 'form_slug_example' # str | The form slug
    form_type = helloasso_python.HelloAssoApiV5ModelsEnumsFormType() # HelloAssoApiV5ModelsEnumsFormType | The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop
    var_from = '2013-10-20T19:20:30+01:00' # datetime | First Date Filter (optional)
    to = '2013-10-20T19:20:30+01:00' # datetime | End Date Filter (exclusive) (optional)
    user_search_key = 'user_search_key_example' # str | Filter results on user or payer first name, last name or email (optional)
    page_index = 1 # int | The page of results to retrieve (optional) (default to 1)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    states = [helloasso_python.HelloAssoApiV5ModelsEnumsPaymentState()] # List[HelloAssoApiV5ModelsEnumsPaymentState] | Filter results by states of payments  Available values: * `Pending` - A payment scheduled at a later date, not yet processed. * `Authorized` - The payment has been authorized, validated, processed. * `Refused` - The payment has been refused by the bank. * `Unknown` * `Registered` - Represents a payment made offline.              Probably for an item of type * `Refunded` - The payment has been refunded. * `Refunding` - The payment is being refunded. * `Contested` - Payment has been contested by the contributor (optional)
    sort_order = helloasso_python.HelloAssoApiV5ModelsEnumsSortOrder() # HelloAssoApiV5ModelsEnumsSortOrder | Sort payments by ascending or descending order. Default is descending (optional)
    sort_field = helloasso_python.HelloAssoApiV5ModelsEnumsSortField() # HelloAssoApiV5ModelsEnumsSortField | Sort payments by a specific field (Date or UpdateDate). Default is date (optional)
    with_count = False # bool | Whether the pagination should include totalCount and totalPages. (optional) (default to False)

    try:
        # Obtenir les informations des paiements effectués sur un formulaire
        api_response = api_instance.organizations_organization_slug_forms_form_type_form_slug_payments_get(organization_slug, form_slug, form_type, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, states=states, sort_order=sort_order, sort_field=sort_field, with_count=with_count)
        print("The response of PaiementsApi->organizations_organization_slug_forms_form_type_form_slug_payments_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaiementsApi->organizations_organization_slug_forms_form_type_form_slug_payments_get: %s\n" % e)
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
 **states** | [**List[HelloAssoApiV5ModelsEnumsPaymentState]**](HelloAssoApiV5ModelsEnumsPaymentState.md)| Filter results by states of payments  Available values: * &#x60;Pending&#x60; - A payment scheduled at a later date, not yet processed. * &#x60;Authorized&#x60; - The payment has been authorized, validated, processed. * &#x60;Refused&#x60; - The payment has been refused by the bank. * &#x60;Unknown&#x60; * &#x60;Registered&#x60; - Represents a payment made offline.              Probably for an item of type * &#x60;Refunded&#x60; - The payment has been refunded. * &#x60;Refunding&#x60; - The payment is being refunded. * &#x60;Contested&#x60; - Payment has been contested by the contributor | [optional] 
 **sort_order** | [**HelloAssoApiV5ModelsEnumsSortOrder**](.md)| Sort payments by ascending or descending order. Default is descending | [optional] 
 **sort_field** | [**HelloAssoApiV5ModelsEnumsSortField**](.md)| Sort payments by a specific field (Date or UpdateDate). Default is date | [optional] 
 **with_count** | **bool**| Whether the pagination should include totalCount and totalPages. | [optional] [default to False]

### Return type

[**ResultsWithPaginationModelPayment**](ResultsWithPaginationModelPayment.md)

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

# **organizations_organization_slug_payments_get**
> organizations_organization_slug_payments_get(organization_slug, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, states=states, sort_order=sort_order, sort_field=sort_field, with_count=with_count)

Obtenir les informations des paiements effectués sur une organisation

Retourne la liste des paiements selon les paramètres<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_payment_state import HelloAssoApiV5ModelsEnumsPaymentState
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_field import HelloAssoApiV5ModelsEnumsSortField
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_order import HelloAssoApiV5ModelsEnumsSortOrder
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
    api_instance = helloasso_python.PaiementsApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization Slug
    var_from = '2013-10-20T19:20:30+01:00' # datetime | First Date Filter (optional)
    to = '2013-10-20T19:20:30+01:00' # datetime | End Date Filter (exclusive) (optional)
    user_search_key = 'user_search_key_example' # str | Filter results on user or payer first name, last name or email (optional)
    page_index = 1 # int | The page of results to retrieve (optional) (default to 1)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    states = [helloasso_python.HelloAssoApiV5ModelsEnumsPaymentState()] # List[HelloAssoApiV5ModelsEnumsPaymentState] | The payment states  Available values: * `Pending` - A payment scheduled at a later date, not yet processed. * `Authorized` - The payment has been authorized, validated, processed. * `Refused` - The payment has been refused by the bank. * `Unknown` * `Registered` - Represents a payment made offline.              Probably for an item of type * `Refunded` - The payment has been refunded. * `Refunding` - The payment is being refunded. * `Contested` - Payment has been contested by the contributor (optional)
    sort_order = helloasso_python.HelloAssoApiV5ModelsEnumsSortOrder() # HelloAssoApiV5ModelsEnumsSortOrder | Sort payments by ascending or descending order. Default is descending (optional)
    sort_field = helloasso_python.HelloAssoApiV5ModelsEnumsSortField() # HelloAssoApiV5ModelsEnumsSortField | Sort payments by a specific field (Date or UpdateDate). Default is date (optional)
    with_count = False # bool | Whether the pagination should include totalCount and totalPages. (optional) (default to False)

    try:
        # Obtenir les informations des paiements effectués sur une organisation
        api_instance.organizations_organization_slug_payments_get(organization_slug, var_from=var_from, to=to, user_search_key=user_search_key, page_index=page_index, page_size=page_size, continuation_token=continuation_token, states=states, sort_order=sort_order, sort_field=sort_field, with_count=with_count)
    except Exception as e:
        print("Exception when calling PaiementsApi->organizations_organization_slug_payments_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization Slug | 
 **var_from** | **datetime**| First Date Filter | [optional] 
 **to** | **datetime**| End Date Filter (exclusive) | [optional] 
 **user_search_key** | **str**| Filter results on user or payer first name, last name or email | [optional] 
 **page_index** | **int**| The page of results to retrieve | [optional] [default to 1]
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **states** | [**List[HelloAssoApiV5ModelsEnumsPaymentState]**](HelloAssoApiV5ModelsEnumsPaymentState.md)| The payment states  Available values: * &#x60;Pending&#x60; - A payment scheduled at a later date, not yet processed. * &#x60;Authorized&#x60; - The payment has been authorized, validated, processed. * &#x60;Refused&#x60; - The payment has been refused by the bank. * &#x60;Unknown&#x60; * &#x60;Registered&#x60; - Represents a payment made offline.              Probably for an item of type * &#x60;Refunded&#x60; - The payment has been refunded. * &#x60;Refunding&#x60; - The payment is being refunded. * &#x60;Contested&#x60; - Payment has been contested by the contributor | [optional] 
 **sort_order** | [**HelloAssoApiV5ModelsEnumsSortOrder**](.md)| Sort payments by ascending or descending order. Default is descending | [optional] 
 **sort_field** | [**HelloAssoApiV5ModelsEnumsSortField**](.md)| Sort payments by a specific field (Date or UpdateDate). Default is date | [optional] 
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

# **organizations_organization_slug_payments_search_get**
> ResultsWithPaginationModelPublicPaymentModel organizations_organization_slug_payments_search_get(organization_slug, var_from=var_from, to=to, page_size=page_size, continuation_token=continuation_token, form_types=form_types, form_type=form_type, states=states, user_id=user_id, search_key=search_key, amount=amount, sort_order=sort_order, sort_field=sort_field)

Rechercher des paiements.

<p>Attention : Le compte total est désactivé, nous retournons la liste des paiements et le continuationToken. </p><p>Recherchez des paiements basés sur de nombreux critères La recherche doit utiliser au moins l'un des paramètres suivants : </p><ul><li>ID de l'organisation : paiements effectués pour cette organisation </li><li>Formulaire : Paiements effectués par ce formulaire en utilisant le couple ID du formulaire et type du formulaire </li><li>ID de l'utilisateur : Paiements effectués par cet utilisateur </li><li>États : Une liste d'états de paiement à filtrer. (si vide, tous les paiements seront retournés)</li><li>Plage de dates : En utilisant du et/ou au </li><li>Requête de recherche : Une liste de mots qui doivent être contenus soit sur les noms des payeurs ou des utilisateurs ou l'email </li><li>Montant du paiement : En centimes, qui doit exactement correspondre au montant des paiements (avec ou sans la contribution) </li></ul><p>L'ordre des résultats est également personnalisable : </p><ul><li>Le champ de tri peut être la date, la date de mise à jour ou la date de création </li><li>L'ordre peut être ascendant ou descendant<br><br><b>Votre token doit avoir l'un de ces rôles : </b><br>OrganizationAdmin<br><br>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br><br><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br> AccessTransactions<br><br></li></ul>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.hello_asso_api_v5_models_enums_payment_state import HelloAssoApiV5ModelsEnumsPaymentState
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_field import HelloAssoApiV5ModelsEnumsSortField
from helloasso_python.models.hello_asso_api_v5_models_enums_sort_order import HelloAssoApiV5ModelsEnumsSortOrder
from helloasso_python.models.results_with_pagination_model_public_payment_model import ResultsWithPaginationModelPublicPaymentModel
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
    api_instance = helloasso_python.PaiementsApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization slug
    var_from = '2013-10-20T19:20:30+01:00' # datetime | First Date Filter (optional)
    to = '2013-10-20T19:20:30+01:00' # datetime | End Date Filter (exclusive) (optional)
    page_size = 20 # int | The number of items to retrieve (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    form_types = [helloasso_python.HelloAssoApiV5ModelsEnumsFormType()] # List[HelloAssoApiV5ModelsEnumsFormType] | The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop (optional)
    form_type = helloasso_python.HelloAssoApiV5ModelsEnumsFormType() # HelloAssoApiV5ModelsEnumsFormType | The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop. This parameter must be used with the parameter formId. (optional)
    states = [helloasso_python.HelloAssoApiV5ModelsEnumsPaymentState()] # List[HelloAssoApiV5ModelsEnumsPaymentState] | Filter results by states of payments  Available values: * `Pending` - A payment scheduled at a later date, not yet processed. * `Authorized` - The payment has been authorized, validated, processed. * `Refused` - The payment has been refused by the bank. * `Unknown` * `Registered` - Represents a payment made offline.              Probably for an item of type * `Refunded` - The payment has been refunded. * `Refunding` - The payment is being refunded. * `Contested` - Payment has been contested by the contributor (optional)
    user_id = 56 # int | The User identifier (optional)
    search_key = 'search_key_example' # str | Filter results on user or payer first name, last name or email. (optional)
    amount = 56 # int | Amount of the payment in cents. Filter payments with exact amount with or without the contribution. (optional)
    sort_order = helloasso_python.HelloAssoApiV5ModelsEnumsSortOrder() # HelloAssoApiV5ModelsEnumsSortOrder | Sort payments by ascending or descending order. Default is descending (optional)
    sort_field = helloasso_python.HelloAssoApiV5ModelsEnumsSortField() # HelloAssoApiV5ModelsEnumsSortField | Sort payments by a specific field (Date or UpdateDate). Default is date (optional)

    try:
        # Rechercher des paiements.
        api_response = api_instance.organizations_organization_slug_payments_search_get(organization_slug, var_from=var_from, to=to, page_size=page_size, continuation_token=continuation_token, form_types=form_types, form_type=form_type, states=states, user_id=user_id, search_key=search_key, amount=amount, sort_order=sort_order, sort_field=sort_field)
        print("The response of PaiementsApi->organizations_organization_slug_payments_search_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaiementsApi->organizations_organization_slug_payments_search_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization slug | 
 **var_from** | **datetime**| First Date Filter | [optional] 
 **to** | **datetime**| End Date Filter (exclusive) | [optional] 
 **page_size** | **int**| The number of items to retrieve | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **form_types** | [**List[HelloAssoApiV5ModelsEnumsFormType]**](HelloAssoApiV5ModelsEnumsFormType.md)| The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop | [optional] 
 **form_type** | [**HelloAssoApiV5ModelsEnumsFormType**](.md)| The form type CrowdFunding, Membership, Event, Donation, PaymentForm, Checkout, Shop. This parameter must be used with the parameter formId. | [optional] 
 **states** | [**List[HelloAssoApiV5ModelsEnumsPaymentState]**](HelloAssoApiV5ModelsEnumsPaymentState.md)| Filter results by states of payments  Available values: * &#x60;Pending&#x60; - A payment scheduled at a later date, not yet processed. * &#x60;Authorized&#x60; - The payment has been authorized, validated, processed. * &#x60;Refused&#x60; - The payment has been refused by the bank. * &#x60;Unknown&#x60; * &#x60;Registered&#x60; - Represents a payment made offline.              Probably for an item of type * &#x60;Refunded&#x60; - The payment has been refunded. * &#x60;Refunding&#x60; - The payment is being refunded. * &#x60;Contested&#x60; - Payment has been contested by the contributor | [optional] 
 **user_id** | **int**| The User identifier | [optional] 
 **search_key** | **str**| Filter results on user or payer first name, last name or email. | [optional] 
 **amount** | **int**| Amount of the payment in cents. Filter payments with exact amount with or without the contribution. | [optional] 
 **sort_order** | [**HelloAssoApiV5ModelsEnumsSortOrder**](.md)| Sort payments by ascending or descending order. Default is descending | [optional] 
 **sort_field** | [**HelloAssoApiV5ModelsEnumsSortField**](.md)| Sort payments by a specific field (Date or UpdateDate). Default is date | [optional] 

### Return type

[**ResultsWithPaginationModelPublicPaymentModel**](ResultsWithPaginationModelPublicPaymentModel.md)

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

# **payments_payment_id_get**
> HelloAssoApiV5ModelsStatisticsPaymentDetail payments_payment_id_get(payment_id, with_failed_refund_operation=with_failed_refund_operation)

Obtenir les informations détaillées d'un paiement.

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>FormAdmin<br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessTransactions<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_statistics_payment_detail import HelloAssoApiV5ModelsStatisticsPaymentDetail
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
    api_instance = helloasso_python.PaiementsApi(api_client)
    payment_id = 56 # int | The payment identifier.
    with_failed_refund_operation = False # bool | True to retrieve the refund operation in the states 'ABORTED', 'CANCELED', 'ERROR', 'REFUSED'. (optional) (default to False)

    try:
        # Obtenir les informations détaillées d'un paiement.
        api_response = api_instance.payments_payment_id_get(payment_id, with_failed_refund_operation=with_failed_refund_operation)
        print("The response of PaiementsApi->payments_payment_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaiementsApi->payments_payment_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payment_id** | **int**| The payment identifier. | 
 **with_failed_refund_operation** | **bool**| True to retrieve the refund operation in the states &#39;ABORTED&#39;, &#39;CANCELED&#39;, &#39;ERROR&#39;, &#39;REFUSED&#39;. | [optional] [default to False]

### Return type

[**HelloAssoApiV5ModelsStatisticsPaymentDetail**](HelloAssoApiV5ModelsStatisticsPaymentDetail.md)

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

# **payments_payment_id_refund_post**
> HelloAssoApiV5ModelsPaymentRefundOperationModel payments_payment_id_refund_post(payment_id, comment=comment, cancel_order=cancel_order, send_refund_mail=send_refund_mail, amount=amount)

Rembourser un paiement.

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/>FormAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> RefundManagement<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_payment_refund_operation_model import HelloAssoApiV5ModelsPaymentRefundOperationModel
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
    api_instance = helloasso_python.PaiementsApi(api_client)
    payment_id = 56 # int | The payment identifier.
    comment = 'comment_example' # str | The comment about this refund. (optional)
    cancel_order = False # bool | Whether the future payments and linked items of this order must be canceled (possible only if the payment is fully refunded) (optional) (default to False)
    send_refund_mail = True # bool | Whether a refund mail must be sent or not. (optional) (default to True)
    amount = 0 # int | The amount in cents to refund. Enter this amount only for a partial refund for stripe. If not filled in then the entire payment is refunded (optional) (default to 0)

    try:
        # Rembourser un paiement.
        api_response = api_instance.payments_payment_id_refund_post(payment_id, comment=comment, cancel_order=cancel_order, send_refund_mail=send_refund_mail, amount=amount)
        print("The response of PaiementsApi->payments_payment_id_refund_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaiementsApi->payments_payment_id_refund_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payment_id** | **int**| The payment identifier. | 
 **comment** | **str**| The comment about this refund. | [optional] 
 **cancel_order** | **bool**| Whether the future payments and linked items of this order must be canceled (possible only if the payment is fully refunded) | [optional] [default to False]
 **send_refund_mail** | **bool**| Whether a refund mail must be sent or not. | [optional] [default to True]
 **amount** | **int**| The amount in cents to refund. Enter this amount only for a partial refund for stripe. If not filled in then the entire payment is refunded | [optional] [default to 0]

### Return type

[**HelloAssoApiV5ModelsPaymentRefundOperationModel**](HelloAssoApiV5ModelsPaymentRefundOperationModel.md)

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

