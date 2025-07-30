# helloasso_python.OrganizationPublicConfigurationsApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**organizations_organization_slug_configurations_get**](OrganizationPublicConfigurationsApi.md#organizations_organization_slug_configurations_get) | **GET** /organizations/{organizationSlug}/configurations | 
[**organizations_organization_slug_configurations_put**](OrganizationPublicConfigurationsApi.md#organizations_organization_slug_configurations_put) | **PUT** /organizations/{organizationSlug}/configurations | 


# **organizations_organization_slug_configurations_get**
> List[HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationModel] organizations_organization_slug_configurations_get(organization_slug)

<br/><br/><b>Your token must have one of these roles : </b><br/>OrganizationAdmin<br/><br/>If you are an <b>association</b>, you can obtain these roles with your client.<br/>If you are a <b>partner</b>, you can obtain these roles by the authorize flow.<br/><br/><b>Your clientId must be allowed all of those privileges : </b> <br/> OrganizationAdministration<br/><br/>

### Example


```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_organizations_organization_public_configuration_model import HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationModel
from helloasso_python.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.helloasso.com/v5
# See configuration.py for a list of all supported configuration parameters.
configuration = helloasso_python.Configuration(
    host = "https://api.helloasso.com/v5"
)


# Enter a context with an instance of the API client
with helloasso_python.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = helloasso_python.OrganizationPublicConfigurationsApi(api_client)
    organization_slug = 'organization_slug_example' # str | 

    try:
        api_response = api_instance.organizations_organization_slug_configurations_get(organization_slug)
        print("The response of OrganizationPublicConfigurationsApi->organizations_organization_slug_configurations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationPublicConfigurationsApi->organizations_organization_slug_configurations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 

### Return type

[**List[HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationModel]**](HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationModel.md)

### Authorization

No authorization required

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

# **organizations_organization_slug_configurations_put**
> organizations_organization_slug_configurations_put(organization_slug, hello_asso_api_v5_models_organizations_organization_public_configurations_request=hello_asso_api_v5_models_organizations_organization_public_configurations_request)

<br/><br/><b>Your token must have one of these roles : </b><br/>OrganizationAdmin<br/><br/>If you are an <b>association</b>, you can obtain these roles with your client.<br/>If you are a <b>partner</b>, you can obtain these roles by the authorize flow.<br/><br/><b>Your clientId must be allowed all of those privileges : </b> <br/> OrganizationAdministration<br/><br/>

### Example


```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_organizations_organization_public_configurations_request import HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationsRequest
from helloasso_python.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.helloasso.com/v5
# See configuration.py for a list of all supported configuration parameters.
configuration = helloasso_python.Configuration(
    host = "https://api.helloasso.com/v5"
)


# Enter a context with an instance of the API client
with helloasso_python.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = helloasso_python.OrganizationPublicConfigurationsApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    hello_asso_api_v5_models_organizations_organization_public_configurations_request = helloasso_python.HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationsRequest() # HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationsRequest |  (optional)

    try:
        api_instance.organizations_organization_slug_configurations_put(organization_slug, hello_asso_api_v5_models_organizations_organization_public_configurations_request=hello_asso_api_v5_models_organizations_organization_public_configurations_request)
    except Exception as e:
        print("Exception when calling OrganizationPublicConfigurationsApi->organizations_organization_slug_configurations_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **hello_asso_api_v5_models_organizations_organization_public_configurations_request** | [**HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationsRequest**](HelloAssoApiV5ModelsOrganizationsOrganizationPublicConfigurationsRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | No Content |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

