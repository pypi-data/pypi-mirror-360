# helloasso_python.FormulairesApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**organizations_organization_slug_form_types_get**](FormulairesApi.md#organizations_organization_slug_form_types_get) | **GET** /organizations/{organizationSlug}/formTypes | Obtenir une liste des types de formulaires pour une organisation
[**organizations_organization_slug_forms_form_type_action_quick_create_post**](FormulairesApi.md#organizations_organization_slug_forms_form_type_action_quick_create_post) | **POST** /organizations/{organizationSlug}/forms/{formType}/action/quick-create | Créer un événement simplifié pour un organisme
[**organizations_organization_slug_forms_form_type_form_slug_public_get**](FormulairesApi.md#organizations_organization_slug_forms_form_type_form_slug_public_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/public | Obtenir des données publiques détaillées sur un formulaire
[**organizations_organization_slug_forms_get**](FormulairesApi.md#organizations_organization_slug_forms_get) | **GET** /organizations/{organizationSlug}/forms | Obtenir les formulaires d&#39;une organisation


# **organizations_organization_slug_form_types_get**
> List[HelloAssoApiV5ModelsEnumsFormType] organizations_organization_slug_form_types_get(organization_slug, states=states)

Obtenir une liste des types de formulaires pour une organisation

Liste tous les types de formulaires où l'organisation possède au moins un formulaire. Cela peut également être filtré par états.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_state import HelloAssoApiV5ModelsEnumsFormState
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
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
    api_instance = helloasso_python.FormulairesApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization Slug
    states = [helloasso_python.HelloAssoApiV5ModelsEnumsFormState()] # List[HelloAssoApiV5ModelsEnumsFormState] | List of Form States to filter with. If none specified, it won't filter results.  Available values: * `Public` - The form is publicly visible and findable on search engines * `Private` - The form is visible only with the URL, you cannot find it on search engines * `Draft` - The form is not yet published but visible if you have admin rights * `Disabled` - The form is disabled and can be reenabled by changing state to public or private (optional)

    try:
        # Obtenir une liste des types de formulaires pour une organisation
        api_response = api_instance.organizations_organization_slug_form_types_get(organization_slug, states=states)
        print("The response of FormulairesApi->organizations_organization_slug_form_types_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormulairesApi->organizations_organization_slug_form_types_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization Slug | 
 **states** | [**List[HelloAssoApiV5ModelsEnumsFormState]**](HelloAssoApiV5ModelsEnumsFormState.md)| List of Form States to filter with. If none specified, it won&#39;t filter results.  Available values: * &#x60;Public&#x60; - The form is publicly visible and findable on search engines * &#x60;Private&#x60; - The form is visible only with the URL, you cannot find it on search engines * &#x60;Draft&#x60; - The form is not yet published but visible if you have admin rights * &#x60;Disabled&#x60; - The form is disabled and can be reenabled by changing state to public or private | [optional] 

### Return type

[**List[HelloAssoApiV5ModelsEnumsFormType]**](HelloAssoApiV5ModelsEnumsFormType.md)

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

# **organizations_organization_slug_forms_form_type_action_quick_create_post**
> HelloAssoApiV5ModelsFormsFormQuickCreateModel organizations_organization_slug_forms_form_type_action_quick_create_post(organization_slug, form_type, hello_asso_api_v5_models_forms_form_quick_create_request=hello_asso_api_v5_models_forms_form_quick_create_request)

Créer un événement simplifié pour un organisme

Permet la création d'un événement avec seulement des informations limitées et quelques tarifications simples. L'événement créé de cette manière peut être modifié ultérieurement avec d'autres services<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> FormAdministration<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.hello_asso_api_v5_models_forms_form_quick_create_model import HelloAssoApiV5ModelsFormsFormQuickCreateModel
from helloasso_python.models.hello_asso_api_v5_models_forms_form_quick_create_request import HelloAssoApiV5ModelsFormsFormQuickCreateRequest
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
    api_instance = helloasso_python.FormulairesApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization Slug
    form_type = helloasso_python.HelloAssoApiV5ModelsEnumsFormType() # HelloAssoApiV5ModelsEnumsFormType | The form type to create - only Event type is supported
    hello_asso_api_v5_models_forms_form_quick_create_request = helloasso_python.HelloAssoApiV5ModelsFormsFormQuickCreateRequest() # HelloAssoApiV5ModelsFormsFormQuickCreateRequest | The body of the request. (optional)

    try:
        # Créer un événement simplifié pour un organisme
        api_response = api_instance.organizations_organization_slug_forms_form_type_action_quick_create_post(organization_slug, form_type, hello_asso_api_v5_models_forms_form_quick_create_request=hello_asso_api_v5_models_forms_form_quick_create_request)
        print("The response of FormulairesApi->organizations_organization_slug_forms_form_type_action_quick_create_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormulairesApi->organizations_organization_slug_forms_form_type_action_quick_create_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization Slug | 
 **form_type** | [**HelloAssoApiV5ModelsEnumsFormType**](.md)| The form type to create - only Event type is supported | 
 **hello_asso_api_v5_models_forms_form_quick_create_request** | [**HelloAssoApiV5ModelsFormsFormQuickCreateRequest**](HelloAssoApiV5ModelsFormsFormQuickCreateRequest.md)| The body of the request. | [optional] 

### Return type

[**HelloAssoApiV5ModelsFormsFormQuickCreateModel**](HelloAssoApiV5ModelsFormsFormQuickCreateModel.md)

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

# **organizations_organization_slug_forms_form_type_form_slug_public_get**
> HelloAssoApiV5ModelsFormsFormPublicModel organizations_organization_slug_forms_form_type_form_slug_public_get(organization_slug, form_type, form_slug)

Obtenir des données publiques détaillées sur un formulaire

Permet de récupérer toutes les informations publiques d'un formulaire, qu'il s'agisse de Crowdfunding, d'Adhésion, d'Événement, de Don...<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.hello_asso_api_v5_models_forms_form_public_model import HelloAssoApiV5ModelsFormsFormPublicModel
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
    api_instance = helloasso_python.FormulairesApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    form_type = helloasso_python.HelloAssoApiV5ModelsEnumsFormType() # HelloAssoApiV5ModelsEnumsFormType | 
    form_slug = 'form_slug_example' # str | 

    try:
        # Obtenir des données publiques détaillées sur un formulaire
        api_response = api_instance.organizations_organization_slug_forms_form_type_form_slug_public_get(organization_slug, form_type, form_slug)
        print("The response of FormulairesApi->organizations_organization_slug_forms_form_type_form_slug_public_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormulairesApi->organizations_organization_slug_forms_form_type_form_slug_public_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **form_type** | [**HelloAssoApiV5ModelsEnumsFormType**](.md)|  | 
 **form_slug** | **str**|  | 

### Return type

[**HelloAssoApiV5ModelsFormsFormPublicModel**](HelloAssoApiV5ModelsFormsFormPublicModel.md)

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

# **organizations_organization_slug_forms_get**
> ResultsWithPaginationModelFormLightModel organizations_organization_slug_forms_get(organization_slug, states=states, form_types=form_types, page_index=page_index, page_size=page_size, continuation_token=continuation_token)

Obtenir les formulaires d'une organisation

Liste tous les formulaires correspondant aux états et types. Si aucun filtre n'est spécifié, aucun filtre n'est appliqué. Les résultats sont classés par date de création en ordre décroissant.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_enums_form_state import HelloAssoApiV5ModelsEnumsFormState
from helloasso_python.models.hello_asso_api_v5_models_enums_form_type import HelloAssoApiV5ModelsEnumsFormType
from helloasso_python.models.results_with_pagination_model_form_light_model import ResultsWithPaginationModelFormLightModel
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
    api_instance = helloasso_python.FormulairesApi(api_client)
    organization_slug = 'organization_slug_example' # str | The organization Slug
    states = [helloasso_python.HelloAssoApiV5ModelsEnumsFormState()] # List[HelloAssoApiV5ModelsEnumsFormState] | States to filter  Available values: * `Public` - The form is publicly visible and findable on search engines * `Private` - The form is visible only with the URL, you cannot find it on search engines * `Draft` - The form is not yet published but visible if you have admin rights * `Disabled` - The form is disabled and can be reenabled by changing state to public or private (optional)
    form_types = [helloasso_python.HelloAssoApiV5ModelsEnumsFormType()] # List[HelloAssoApiV5ModelsEnumsFormType] | Types to filter (optional)
    page_index = 1 # int | The page of results to retrieve (optional) (default to 1)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)

    try:
        # Obtenir les formulaires d'une organisation
        api_response = api_instance.organizations_organization_slug_forms_get(organization_slug, states=states, form_types=form_types, page_index=page_index, page_size=page_size, continuation_token=continuation_token)
        print("The response of FormulairesApi->organizations_organization_slug_forms_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormulairesApi->organizations_organization_slug_forms_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**| The organization Slug | 
 **states** | [**List[HelloAssoApiV5ModelsEnumsFormState]**](HelloAssoApiV5ModelsEnumsFormState.md)| States to filter  Available values: * &#x60;Public&#x60; - The form is publicly visible and findable on search engines * &#x60;Private&#x60; - The form is visible only with the URL, you cannot find it on search engines * &#x60;Draft&#x60; - The form is not yet published but visible if you have admin rights * &#x60;Disabled&#x60; - The form is disabled and can be reenabled by changing state to public or private | [optional] 
 **form_types** | [**List[HelloAssoApiV5ModelsEnumsFormType]**](HelloAssoApiV5ModelsEnumsFormType.md)| Types to filter | [optional] 
 **page_index** | **int**| The page of results to retrieve | [optional] [default to 1]
 **page_size** | **int**| The number of items per page | [optional] [default to 20]
 **continuation_token** | **str**| Continuation Token from which we wish to retrieve results | [optional] 

### Return type

[**ResultsWithPaginationModelFormLightModel**](ResultsWithPaginationModelFormLightModel.md)

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

