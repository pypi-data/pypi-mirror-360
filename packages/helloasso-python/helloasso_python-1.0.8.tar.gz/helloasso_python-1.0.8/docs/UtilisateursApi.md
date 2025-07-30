# helloasso_python.UtilisateursApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**users_me_organizations_get**](UtilisateursApi.md#users_me_organizations_get) | **GET** /users/me/organizations | Obtenir mes organisations


# **users_me_organizations_get**
> List[HelloAssoApiV5ModelsOrganizationOrganizationLightModel] users_me_organizations_get()

Obtenir mes organisations

Renvoie la liste des organisations où l'utilisateur connecté a des droits<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> AccessPublicData<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_organization_organization_light_model import HelloAssoApiV5ModelsOrganizationOrganizationLightModel
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
    api_instance = helloasso_python.UtilisateursApi(api_client)

    try:
        # Obtenir mes organisations
        api_response = api_instance.users_me_organizations_get()
        print("The response of UtilisateursApi->users_me_organizations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UtilisateursApi->users_me_organizations_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[HelloAssoApiV5ModelsOrganizationOrganizationLightModel]**](HelloAssoApiV5ModelsOrganizationOrganizationLightModel.md)

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

