# helloasso_python.ListeDeValeursApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**values_company_legal_status_get**](ListeDeValeursApi.md#values_company_legal_status_get) | **GET** /values/company-legal-status | Obtenir la liste des statuts juridiques
[**values_organization_categories_get**](ListeDeValeursApi.md#values_organization_categories_get) | **GET** /values/organization/categories | Obtenir la liste des catégories du JO
[**values_tags_get**](ListeDeValeursApi.md#values_tags_get) | **GET** /values/tags | Obtenir la liste des tags publiques


# **values_company_legal_status_get**
> List[HelloAssoApiV5ModelsAccountCompanyLegalStatusModel] values_company_legal_status_get()

Obtenir la liste des statuts juridiques

<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_account_company_legal_status_model import HelloAssoApiV5ModelsAccountCompanyLegalStatusModel
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
    api_instance = helloasso_python.ListeDeValeursApi(api_client)

    try:
        # Obtenir la liste des statuts juridiques
        api_response = api_instance.values_company_legal_status_get()
        print("The response of ListeDeValeursApi->values_company_legal_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ListeDeValeursApi->values_company_legal_status_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[HelloAssoApiV5ModelsAccountCompanyLegalStatusModel]**](HelloAssoApiV5ModelsAccountCompanyLegalStatusModel.md)

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

# **values_organization_categories_get**
> List[HelloAssoApiV5ModelsAccountOrganismCategoryModel] values_organization_categories_get()

Obtenir la liste des catégories du JO

Utilisez ceci afin de construire votre liste de catégories d'organisation<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_account_organism_category_model import HelloAssoApiV5ModelsAccountOrganismCategoryModel
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
    api_instance = helloasso_python.ListeDeValeursApi(api_client)

    try:
        # Obtenir la liste des catégories du JO
        api_response = api_instance.values_organization_categories_get()
        print("The response of ListeDeValeursApi->values_organization_categories_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ListeDeValeursApi->values_organization_categories_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[HelloAssoApiV5ModelsAccountOrganismCategoryModel]**](HelloAssoApiV5ModelsAccountOrganismCategoryModel.md)

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

# **values_tags_get**
> List[HelloAssoApiV5ModelsTagsPublicTagModel] values_tags_get()

Obtenir la liste des tags publiques

Utilisez ceci afin de récupérer la liste des étiquettes utilisées<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_tags_public_tag_model import HelloAssoApiV5ModelsTagsPublicTagModel
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
    api_instance = helloasso_python.ListeDeValeursApi(api_client)

    try:
        # Obtenir la liste des tags publiques
        api_response = api_instance.values_tags_get()
        print("The response of ListeDeValeursApi->values_tags_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ListeDeValeursApi->values_tags_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[HelloAssoApiV5ModelsTagsPublicTagModel]**](HelloAssoApiV5ModelsTagsPublicTagModel.md)

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

