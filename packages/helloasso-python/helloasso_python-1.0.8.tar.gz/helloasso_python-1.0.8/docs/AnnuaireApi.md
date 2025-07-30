# helloasso_python.AnnuaireApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**directory_forms_post**](AnnuaireApi.md#directory_forms_post) | **POST** /directory/forms | Récupérer les formulaires
[**directory_organizations_post**](AnnuaireApi.md#directory_organizations_post) | **POST** /directory/organizations | Récupérer les organisations


# **directory_forms_post**
> ResultsWithPaginationModelSynchronizableFormModel directory_forms_post(page_size=page_size, continuation_token=continuation_token, hello_asso_api_v5_models_directory_list_forms_request=hello_asso_api_v5_models_directory_list_forms_request)

Récupérer les formulaires

Permet de récupérer une liste de tous les formulaires visibles correspondant à tous les filtres de l'annuaire jusqu'à ce qu'il soit synchronisé (en utilisant le continuationToken). Si aucun filtre n'est spécifié, aucun filtre n'est appliqué. Les résultats sont classés par date de mise à jour de la visibilité API en ordre croissant. Une fois la liste synchronisée, seuls les formulaires avec une date de mise à jour de la visibilité API supérieure à la dernière forme envoyée sont retournés (toujours en utilisant le continuationToken). Cela concerne les nouveaux formulaires à insérer (souhaitant apparaître de l'annuaire) ainsi que les anciens à supprimer (ne souhaitant plus apparaître dans l'annuaire). Le nombre total de résultats (ou de pages) n'est pas récupérable, donc les informations de pagination retournées indiqueront toujours -1.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> FormOpenDirectory<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_directory_list_forms_request import HelloAssoApiV5ModelsDirectoryListFormsRequest
from helloasso_python.models.results_with_pagination_model_synchronizable_form_model import ResultsWithPaginationModelSynchronizableFormModel
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
    api_instance = helloasso_python.AnnuaireApi(api_client)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    hello_asso_api_v5_models_directory_list_forms_request = helloasso_python.HelloAssoApiV5ModelsDirectoryListFormsRequest() # HelloAssoApiV5ModelsDirectoryListFormsRequest | Body which contains the filters to apply (optional)

    try:
        # Récupérer les formulaires
        api_response = api_instance.directory_forms_post(page_size=page_size, continuation_token=continuation_token, hello_asso_api_v5_models_directory_list_forms_request=hello_asso_api_v5_models_directory_list_forms_request)
        print("The response of AnnuaireApi->directory_forms_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnnuaireApi->directory_forms_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **hello_asso_api_v5_models_directory_list_forms_request** | [**HelloAssoApiV5ModelsDirectoryListFormsRequest**](HelloAssoApiV5ModelsDirectoryListFormsRequest.md)| Body which contains the filters to apply | [optional] 

### Return type

[**ResultsWithPaginationModelSynchronizableFormModel**](ResultsWithPaginationModelSynchronizableFormModel.md)

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

# **directory_organizations_post**
> ResultsWithPaginationModelSynchronizableOrganizationModel directory_organizations_post(page_size=page_size, continuation_token=continuation_token, hello_asso_api_v5_models_directory_list_organizations_request=hello_asso_api_v5_models_directory_list_organizations_request)

Récupérer les organisations

Permet de récupérer une liste de toutes les organisations visibles correspondant à tous les filtres de l'annuaire jusqu'à ce qu'il soit synchronisé (en utilisant le continuationToken). Si aucun filtre n'est spécifié, aucun filtre n'est appliqué. Les résultats sont classés par date de mise à jour de la visibilité API en ordre croissant. Une fois la liste synchronisée, seules les organisations avec une date de mise à jour de la visibilité API supérieure à la dernière organisation envoyée sont retournées (toujours en utilisant le continuationToken). Cela concerne les nouvelles organisations à insérer (souhaitant apparaître dans l'annuaire) ainsi que les anciennes à supprimer (ne souhaitant plus apparaître dans l'annuaire). Le nombre total de résultats (ou de pages) n'est pas récupérable, donc les informations de pagination retournées indiqueront toujours -1.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> OrganizationOpenDirectory<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_directory_list_organizations_request import HelloAssoApiV5ModelsDirectoryListOrganizationsRequest
from helloasso_python.models.results_with_pagination_model_synchronizable_organization_model import ResultsWithPaginationModelSynchronizableOrganizationModel
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
    api_instance = helloasso_python.AnnuaireApi(api_client)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    hello_asso_api_v5_models_directory_list_organizations_request = helloasso_python.HelloAssoApiV5ModelsDirectoryListOrganizationsRequest() # HelloAssoApiV5ModelsDirectoryListOrganizationsRequest | Body which contains the filters to apply (optional)

    try:
        # Récupérer les organisations
        api_response = api_instance.directory_organizations_post(page_size=page_size, continuation_token=continuation_token, hello_asso_api_v5_models_directory_list_organizations_request=hello_asso_api_v5_models_directory_list_organizations_request)
        print("The response of AnnuaireApi->directory_organizations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnnuaireApi->directory_organizations_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 
 **hello_asso_api_v5_models_directory_list_organizations_request** | [**HelloAssoApiV5ModelsDirectoryListOrganizationsRequest**](HelloAssoApiV5ModelsDirectoryListOrganizationsRequest.md)| Body which contains the filters to apply | [optional] 

### Return type

[**ResultsWithPaginationModelSynchronizableOrganizationModel**](ResultsWithPaginationModelSynchronizableOrganizationModel.md)

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

