# helloasso_python.ReusFiscauxApi

All URIs are relative to *https://api.helloasso.com/v5*

Method | HTTP request | Description
------------- | ------------- | -------------
[**organizations_organization_slug_tax_receipt_configuration_get**](ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_configuration_get) | **GET** /organizations/{organizationSlug}/tax-receipt/configuration | Obtenir la configuration des reçus fiscaux
[**organizations_organization_slug_tax_receipt_configuration_put**](ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_configuration_put) | **PUT** /organizations/{organizationSlug}/tax-receipt/configuration | Mettre à jour la configuration des reçus fiscaux
[**organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put**](ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put) | **PUT** /organizations/{organizationSlug}/tax-receipt/fiscal-receipt-transmitter | Mettre à jour l&#39;émetteur des reçus fiscaux
[**organizations_organization_slug_tax_receipt_preview_post**](ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_preview_post) | **POST** /organizations/{organizationSlug}/tax-receipt/preview | Prévisualiser les reçus fiscaux


# **organizations_organization_slug_tax_receipt_configuration_get**
> HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration organizations_organization_slug_tax_receipt_configuration_get(organization_slug)

Obtenir la configuration des reçus fiscaux

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/>FormAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> RefundManagement<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_core_accounts_tax_receipts_organization_fiscal_receipt_options_configuration import HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration
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
    api_instance = helloasso_python.ReusFiscauxApi(api_client)
    organization_slug = 'organization_slug_example' # str | 

    try:
        # Obtenir la configuration des reçus fiscaux
        api_response = api_instance.organizations_organization_slug_tax_receipt_configuration_get(organization_slug)
        print("The response of ReusFiscauxApi->organizations_organization_slug_tax_receipt_configuration_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReusFiscauxApi->organizations_organization_slug_tax_receipt_configuration_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 

### Return type

[**HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration**](HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration.md)

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

# **organizations_organization_slug_tax_receipt_configuration_put**
> organizations_organization_slug_tax_receipt_configuration_put(organization_slug, file, config=config)

Mettre à jour la configuration des reçus fiscaux

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
    api_instance = helloasso_python.ReusFiscauxApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    file = None # bytearray | Upload File
    config = 'config_example' # str | config (optional)

    try:
        # Mettre à jour la configuration des reçus fiscaux
        api_instance.organizations_organization_slug_tax_receipt_configuration_put(organization_slug, file, config=config)
    except Exception as e:
        print("Exception when calling ReusFiscauxApi->organizations_organization_slug_tax_receipt_configuration_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **file** | **bytearray**| Upload File | 
 **config** | **str**| config | [optional] 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |
**404** | Not Found |  -  |
**415** | Client Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put**
> organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put(organization_slug, hello_asso_api_v5_models_organization_legal_informations_update_organization_fiscal_receipt_transmitter_body=hello_asso_api_v5_models_organization_legal_informations_update_organization_fiscal_receipt_transmitter_body)

Mettre à jour l'émetteur des reçus fiscaux

<br/><br/><b>Votre token doit avoir l'un de ces rôles : </b><br/>OrganizationAdmin<br/>FormAdmin<br/><br/>Si vous êtes une <b>association</b>, vous pouvez obtenir ces rôles avec votre client.<br/>Si vous êtes un <b>partenaire</b>, vous pouvez obtenir ces rôles par le flux d'autorisation.<br/><br/><b>Votre clientId doit être autorisé à tous ces privilèges : </b> <br/> RefundManagement<br/><br/>

### Example

* OAuth Authentication (OAuth2):

```python
import helloasso_python
from helloasso_python.models.hello_asso_api_v5_models_organization_legal_informations_update_organization_fiscal_receipt_transmitter_body import HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationFiscalReceiptTransmitterBody
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
    api_instance = helloasso_python.ReusFiscauxApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    hello_asso_api_v5_models_organization_legal_informations_update_organization_fiscal_receipt_transmitter_body = helloasso_python.HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationFiscalReceiptTransmitterBody() # HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationFiscalReceiptTransmitterBody |  (optional)

    try:
        # Mettre à jour l'émetteur des reçus fiscaux
        api_instance.organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put(organization_slug, hello_asso_api_v5_models_organization_legal_informations_update_organization_fiscal_receipt_transmitter_body=hello_asso_api_v5_models_organization_legal_informations_update_organization_fiscal_receipt_transmitter_body)
    except Exception as e:
        print("Exception when calling ReusFiscauxApi->organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **hello_asso_api_v5_models_organization_legal_informations_update_organization_fiscal_receipt_transmitter_body** | [**HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationFiscalReceiptTransmitterBody**](HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationFiscalReceiptTransmitterBody.md)|  | [optional] 

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

# **organizations_organization_slug_tax_receipt_preview_post**
> organizations_organization_slug_tax_receipt_preview_post(organization_slug, file, config=config)

Prévisualiser les reçus fiscaux

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
    api_instance = helloasso_python.ReusFiscauxApi(api_client)
    organization_slug = 'organization_slug_example' # str | 
    file = None # bytearray | Upload File
    config = 'config_example' # str | config (optional)

    try:
        # Prévisualiser les reçus fiscaux
        api_instance.organizations_organization_slug_tax_receipt_preview_post(organization_slug, file, config=config)
    except Exception as e:
        print("Exception when calling ReusFiscauxApi->organizations_organization_slug_tax_receipt_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_slug** | **str**|  | 
 **file** | **bytearray**| Upload File | 
 **config** | **str**| config | [optional] 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized, you must add a valid JWT into Authorization Header with the format : &#x60;Bearer TOKEN&#x60; |  -  |
**403** | The JWT token hasn&#39;t the privileges or Roles for this action |  -  |
**415** | Client Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

