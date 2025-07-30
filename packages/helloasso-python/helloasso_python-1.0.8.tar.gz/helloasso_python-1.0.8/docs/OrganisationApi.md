# helloasso_python.OrganisationApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**organizations_legal_informations_legal_structures_get**](OrganisationApi.md#organizations_legal_informations_legal_structures_get) | **GET** /organizations/legal-informations/legal-structures | Obtenir la structure juridique d&#39;une organisation visible.
[**organizations_legal_informations_organization_slug_configuration_get**](OrganisationApi.md#organizations_legal_informations_organization_slug_configuration_get) | **GET** /organizations/legal-informations/{organizationSlug}/configuration | Obtenir la configuration des informations juridiques de l&#39;organisation.
[**organizations_legal_informations_organization_slug_configuration_put**](OrganisationApi.md#organizations_legal_informations_organization_slug_configuration_put) | **PUT** /organizations/legal-informations/{organizationSlug}/configuration | Mettre à jour la configuration des informations juridiques de l&#39;organisation.
[**organizations_legal_informations_tax_information_texts_get**](OrganisationApi.md#organizations_legal_informations_tax_information_texts_get) | **GET** /organizations/legal-informations/tax-information-texts | Obtenir les textes d&#39;information fiscale de l&#39;organisation.
[**organizations_organization_slug_get**](OrganisationApi.md#organizations_organization_slug_get) | **GET** /organizations/{organizationSlug} | Obtenir le détail d&#39;une organisation


# **organizations_legal_informations_legal_structures_get**
> List[HelloAssoApiV5ModelsOrganizationLegalInformationsOrganizationLegalStructuresModel] organizations_legal_informations_legal_structures_get()

Obtenir la structure juridique d'une organisation visible.

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> OrganizationAdministration<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_organization_legal_informations_organization_legal_structures_model import HelloAssoApiV5ModelsOrganizationLegalInformationsOrganizationLegalStructuresModel
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
    api_instance = helloasso_python.OrganisationApi(api_client)

    try:
        # Obtenir la structure juridique d'une organisation visible.
        api_response = api_instance.organizations_legal_informations_legal_structures_get()
        print("The response of OrganisationApi->organizations_legal_informations_legal_structures_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganisationApi->organizations_legal_informations_legal_structures_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[HelloAssoApiV5ModelsOrganizationLegalInformationsOrganizationLegalStructuresModel]**](HelloAssoApiV5ModelsOrganizationLegalInformationsOrganizationLegalStructuresModel.md)

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
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **organizations_legal_informations_organization_slug_configuration_get**
> HelloAssoModelsAccountsOrganizationLegalInformationsOrganizationLegalInformationConfiguration organizations_legal_informations_organization_slug_configuration_get(organization_slug)

Obtenir la configuration des informations juridiques de l'organisation.

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> OrganizationAdministration<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_models_accounts_organization_legal_informations_organization_legal_information_configuration import HelloAssoModelsAccountsOrganizationLegalInformationsOrganizationLegalInformationConfiguration
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
    api_instance = helloasso_python.OrganisationApi(api_client)
    organization_slug = 'organization_slug_example' # str | 

    try:
        # Obtenir la configuration des informations juridiques de l'organisation.
        api_response = api_instance.organizations_legal_informations_organization_slug_configuration_get(organization_slug)
        print("The response of OrganisationApi->organizations_legal_informations_organization_slug_configuration_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganisationApi->organizations_legal_informations_organization_slug_configuration_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 

### Return type

[**HelloAssoModelsAccountsOrganizationLegalInformationsOrganizationLegalInformationConfiguration**](HelloAssoModelsAccountsOrganizationLegalInformationsOrganizationLegalInformationConfiguration.md)

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
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **organizations_legal_informations_organization_slug_configuration_put**
> organizations_legal_informations_organization_slug_configuration_put(organization_slug, hello_asso_api_v5_models_organization_legal_informations_update_organization_legal_information_configuration_body=hello_asso_api_v5_models_organization_legal_informations_update_organization_legal_information_configuration_body)

Mettre à jour la configuration des informations juridiques de l'organisation.

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> OrganizationAdministration<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_organization_legal_informations_update_organization_legal_information_configuration_body import HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationLegalInformationConfigurationBody
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
    api_instance = helloasso_python.OrganisationApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    hello_asso_api_v5_models_organization_legal_informations_update_organization_legal_information_configuration_body = helloasso_python.HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationLegalInformationConfigurationBody() # HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationLegalInformationConfigurationBody |  (optional)

    try:
        # Mettre à jour la configuration des informations juridiques de l'organisation.
        api_instance.organizations_legal_informations_organization_slug_configuration_put(organization_slug, hello_asso_api_v5_models_organization_legal_informations_update_organization_legal_information_configuration_body=hello_asso_api_v5_models_organization_legal_informations_update_organization_legal_information_configuration_body)
    except Exception as e:
        print("Exception when calling OrganisationApi->organizations_legal_informations_organization_slug_configuration_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **hello_asso_api_v5_models_organization_legal_informations_update_organization_legal_information_configuration_body** | [**HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationLegalInformationConfigurationBody**](HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationLegalInformationConfigurationBody.md)|  | [optional] 

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
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **organizations_legal_informations_tax_information_texts_get**
> List[HelloAssoModelsAccountsOrganizationLegalInformationsTaxInformationText] organizations_legal_informations_tax_information_texts_get(organization_slug=organization_slug)

Obtenir les textes d'information fiscale de l'organisation.

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> OrganizationAdministration<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_models_accounts_organization_legal_informations_tax_information_text import HelloAssoModelsAccountsOrganizationLegalInformationsTaxInformationText
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
    api_instance = helloasso_python.OrganisationApi(api_client)
    organization_slug = 'organization_slug_example' # str |  (optional)

    try:
        # Obtenir les textes d'information fiscale de l'organisation.
        api_response = api_instance.organizations_legal_informations_tax_information_texts_get(organization_slug=organization_slug)
        print("The response of OrganisationApi->organizations_legal_informations_tax_information_texts_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganisationApi->organizations_legal_informations_tax_information_texts_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | [optional] 

### Return type

[**List[HelloAssoModelsAccountsOrganizationLegalInformationsTaxInformationText]**](HelloAssoModelsAccountsOrganizationLegalInformationsTaxInformationText.md)

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
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **organizations_organization_slug_get**
> HelloAssoApiV5ModelsOrganizationOrganizationModel organizations_organization_slug_get(organization_slug)

Obtenir le détail d'une organisation

Obtenir les informations publiques de l'organisation spécifiée.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_organization_organization_model import HelloAssoApiV5ModelsOrganizationOrganizationModel
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
    api_instance = helloasso_python.OrganisationApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization Slug

    try:
        # Obtenir le détail d'une organisation
        api_response = api_instance.organizations_organization_slug_get(organization_slug)
        print("The response of OrganisationApi->organizations_organization_slug_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganisationApi->organizations_organization_slug_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization Slug | 

### Return type

[**HelloAssoApiV5ModelsOrganizationOrganizationModel**](HelloAssoApiV5ModelsOrganizationOrganizationModel.md)

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

