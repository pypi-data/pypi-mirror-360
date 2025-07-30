# helloasso_python.PartenairesApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**partners_me_api_clients_put**](PartenairesApi.md#partners_me_api_clients_put) | **PUT** /partners/me/api-clients | Mise à jour du domaine
[**partners_me_api_notifications_delete**](PartenairesApi.md#partners_me_api_notifications_delete) | **DELETE** /partners/me/api-notifications | Suppression de l&#39;URL de notification principale
[**partners_me_api_notifications_organizations_organization_slug_delete**](PartenairesApi.md#partners_me_api_notifications_organizations_organization_slug_delete) | **DELETE** /partners/me/api-notifications/organizations/{organizationSlug} | Suppression d&#39;une URL de notification liée à une organisation
[**partners_me_api_notifications_organizations_organization_slug_put**](PartenairesApi.md#partners_me_api_notifications_organizations_organization_slug_put) | **PUT** /partners/me/api-notifications/organizations/{organizationSlug} | Mise à jour d&#39;une URL de notification liée à une organisation
[**partners_me_api_notifications_put**](PartenairesApi.md#partners_me_api_notifications_put) | **PUT** /partners/me/api-notifications | Mise à jour de l&#39;URL de notification principale
[**partners_me_get**](PartenairesApi.md#partners_me_get) | **GET** /partners/me | Récupération des informations
[**partners_me_organizations_get**](PartenairesApi.md#partners_me_organizations_get) | **GET** /partners/me/organizations | Obtenir toutes les organisations


# **partners_me_api_clients_put**
> partners_me_api_clients_put(hello_asso_api_v5_models_accounts_clients_public_put_api_client_request=hello_asso_api_v5_models_accounts_clients_public_put_api_client_request)

Mise à jour du domaine

<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_accounts_clients_public_put_api_client_request import HelloAssoApiV5ModelsAccountsClientsPublicPutApiClientRequest
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
    api_instance = helloasso_python.PartenairesApi(api_client)
    hello_asso_api_v5_models_accounts_clients_public_put_api_client_request = helloasso_python.HelloAssoApiV5ModelsAccountsClientsPublicPutApiClientRequest() # HelloAssoApiV5ModelsAccountsClientsPublicPutApiClientRequest |  (optional)

    try:
        # Mise à jour du domaine
        api_instance.partners_me_api_clients_put(hello_asso_api_v5_models_accounts_clients_public_put_api_client_request=hello_asso_api_v5_models_accounts_clients_public_put_api_client_request)
    except Exception as e:
        print("Exception when calling PartenairesApi->partners_me_api_clients_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hello_asso_api_v5_models_accounts_clients_public_put_api_client_request** | [**HelloAssoApiV5ModelsAccountsClientsPublicPutApiClientRequest**](HelloAssoApiV5ModelsAccountsClientsPublicPutApiClientRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **partners_me_api_notifications_delete**
> partners_me_api_notifications_delete(notification_type=notification_type)

Suppression de l'URL de notification principale

<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_api_notifications_api_notification_type import HelloAssoApiV5ModelsApiNotificationsApiNotificationType
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
    api_instance = helloasso_python.PartenairesApi(api_client)
    notification_type = helloasso_python.HelloAssoApiV5ModelsApiNotificationsApiNotificationType() # HelloAssoApiV5ModelsApiNotificationsApiNotificationType | Do not specify a notification type to remove the main notification Url (optional)

    try:
        # Suppression de l'URL de notification principale
        api_instance.partners_me_api_notifications_delete(notification_type=notification_type)
    except Exception as e:
        print("Exception when calling PartenairesApi->partners_me_api_notifications_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_type** | [**HelloAssoApiV5ModelsApiNotificationsApiNotificationType**](.md)| Do not specify a notification type to remove the main notification Url | [optional] 

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

# **partners_me_api_notifications_organizations_organization_slug_delete**
> partners_me_api_notifications_organizations_organization_slug_delete(organization_slug, notification_type=notification_type)

Suppression d'une URL de notification liée à une organisation

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_api_notifications_api_notification_type import HelloAssoApiV5ModelsApiNotificationsApiNotificationType
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
    api_instance = helloasso_python.PartenairesApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    notification_type = helloasso_python.HelloAssoApiV5ModelsApiNotificationsApiNotificationType() # HelloAssoApiV5ModelsApiNotificationsApiNotificationType | Do not specify a notification type to remove the main notification Url (optional)

    try:
        # Suppression d'une URL de notification liée à une organisation
        api_instance.partners_me_api_notifications_organizations_organization_slug_delete(organization_slug, notification_type=notification_type)
    except Exception as e:
        print("Exception when calling PartenairesApi->partners_me_api_notifications_organizations_organization_slug_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **notification_type** | [**HelloAssoApiV5ModelsApiNotificationsApiNotificationType**](.md)| Do not specify a notification type to remove the main notification Url | [optional] 

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

# **partners_me_api_notifications_organizations_organization_slug_put**
> HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel partners_me_api_notifications_organizations_organization_slug_put(organization_slug, hello_asso_api_v5_models_api_notifications_post_api_url_notification_body=hello_asso_api_v5_models_api_notifications_post_api_url_notification_body)

Mise à jour d'une URL de notification liée à une organisation

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_api_notifications_api_url_notification_model import HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel
from helloasso_python.models.hello_asso_api_v5_models_api_notifications_post_api_url_notification_body import HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody
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
    api_instance = helloasso_python.PartenairesApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    hello_asso_api_v5_models_api_notifications_post_api_url_notification_body = helloasso_python.HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody() # HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody | The body of the request, do not specify a notification type to update the main notification Url (optional)

    try:
        # Mise à jour d'une URL de notification liée à une organisation
        api_response = api_instance.partners_me_api_notifications_organizations_organization_slug_put(organization_slug, hello_asso_api_v5_models_api_notifications_post_api_url_notification_body=hello_asso_api_v5_models_api_notifications_post_api_url_notification_body)
        print("The response of PartenairesApi->partners_me_api_notifications_organizations_organization_slug_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartenairesApi->partners_me_api_notifications_organizations_organization_slug_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **hello_asso_api_v5_models_api_notifications_post_api_url_notification_body** | [**HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody**](HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody.md)| The body of the request, do not specify a notification type to update the main notification Url | [optional] 

### Return type

[**HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel**](HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel.md)

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

# **partners_me_api_notifications_put**
> HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel partners_me_api_notifications_put(hello_asso_api_v5_models_api_notifications_post_api_url_notification_body=hello_asso_api_v5_models_api_notifications_post_api_url_notification_body)

Mise à jour de l'URL de notification principale

<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_api_notifications_api_url_notification_model import HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel
from helloasso_python.models.hello_asso_api_v5_models_api_notifications_post_api_url_notification_body import HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody
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
    api_instance = helloasso_python.PartenairesApi(api_client)
    hello_asso_api_v5_models_api_notifications_post_api_url_notification_body = helloasso_python.HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody() # HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody | The body of the request, do not specify a notification type to update the main notification Url (optional)

    try:
        # Mise à jour de l'URL de notification principale
        api_response = api_instance.partners_me_api_notifications_put(hello_asso_api_v5_models_api_notifications_post_api_url_notification_body=hello_asso_api_v5_models_api_notifications_post_api_url_notification_body)
        print("The response of PartenairesApi->partners_me_api_notifications_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartenairesApi->partners_me_api_notifications_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hello_asso_api_v5_models_api_notifications_post_api_url_notification_body** | [**HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody**](HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody.md)| The body of the request, do not specify a notification type to update the main notification Url | [optional] 

### Return type

[**HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel**](HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel.md)

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

# **partners_me_get**
> HelloAssoApiV5ModelsPartnersPartnerPublicModel partners_me_get()

Récupération des informations

<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_partners_partner_public_model import HelloAssoApiV5ModelsPartnersPartnerPublicModel
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
    api_instance = helloasso_python.PartenairesApi(api_client)

    try:
        # Récupération des informations
        api_response = api_instance.partners_me_get()
        print("The response of PartenairesApi->partners_me_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartenairesApi->partners_me_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HelloAssoApiV5ModelsPartnersPartnerPublicModel**](HelloAssoApiV5ModelsPartnersPartnerPublicModel.md)

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

# **partners_me_organizations_get**
> ResultsWithPaginationModelPartnerOrganizationModel partners_me_organizations_get(page_size=page_size, continuation_token=continuation_token)

Obtenir toutes les organisations

Liste toutes les organisations liées au partenaire. Les résultats sont classés par date de mise à jour de la visibilité API en ordre croissant. Le nombre total de résultats (ou de pages) n'est pas récupérable, donc les informations de pagination retournées indiqueront toujours -1.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.results_with_pagination_model_partner_organization_model import ResultsWithPaginationModelPartnerOrganizationModel
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
    api_instance = helloasso_python.PartenairesApi(api_client)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)

    try:
        # Obtenir toutes les organisations
        api_response = api_instance.partners_me_organizations_get(page_size=page_size, continuation_token=continuation_token)
        print("The response of PartenairesApi->partners_me_organizations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartenairesApi->partners_me_organizations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 

### Return type

[**ResultsWithPaginationModelPartnerOrganizationModel**](ResultsWithPaginationModelPartnerOrganizationModel.md)

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

