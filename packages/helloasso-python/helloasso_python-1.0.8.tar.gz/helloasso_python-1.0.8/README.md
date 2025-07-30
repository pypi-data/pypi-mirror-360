# helloasso-python

The HelloAsso Python library offers a straightforward way to interact with the HelloAsso API in Python applications. It features a collection of pre-built classes for API resources that automatically adapt to API responses, ensuring flexibility across different versions of the HelloAsso API.

## Requirements.

Python 3.8+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install helloasso-python
```
(you may need to run `pip` with root permission: `sudo pip install helloasso-python`)

Then import the package:
```python
import helloasso_python
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import helloasso_python
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

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
    api_instance = helloasso_python.AnnuaireApi(api_client)
    page_size = 20 # int | The number of items per page (optional) (default to 20)
    continuation_token = 'continuation_token_example' # str | Continuation Token from which we wish to retrieve results (optional)
    hello_asso_api_v5_models_directory_list_forms_request = helloasso_python.HelloAssoApiV5ModelsDirectoryListFormsRequest() # HelloAssoApiV5ModelsDirectoryListFormsRequest | Body which contains the filters to apply (optional)

    try:
        # Récupérer les formulaires
        api_response = api_instance.directory_forms_post(page_size=page_size, continuation_token=continuation_token, hello_asso_api_v5_models_directory_list_forms_request=hello_asso_api_v5_models_directory_list_forms_request)
        print("The response of AnnuaireApi->directory_forms_post:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AnnuaireApi->directory_forms_post: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.helloasso.com/v5*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AnnuaireApi* | [**directory_forms_post**](docs/AnnuaireApi.md#directory_forms_post) | **POST** /directory/forms | Récupérer les formulaires
*AnnuaireApi* | [**directory_organizations_post**](docs/AnnuaireApi.md#directory_organizations_post) | **POST** /directory/organizations | Récupérer les organisations
*CheckoutApi* | [**organizations_organization_slug_checkout_intents_checkout_intent_id_get**](docs/CheckoutApi.md#organizations_organization_slug_checkout_intents_checkout_intent_id_get) | **GET** /organizations/{organizationSlug}/checkout-intents/{checkoutIntentId} | Récupérer une intention de paiement
*CheckoutApi* | [**organizations_organization_slug_checkout_intents_post**](docs/CheckoutApi.md#organizations_organization_slug_checkout_intents_post) | **POST** /organizations/{organizationSlug}/checkout-intents | Initialisation d&#39;un Checkout
*CommandesApi* | [**items_item_id_get**](docs/CommandesApi.md#items_item_id_get) | **GET** /items/{itemId} | Obtenir le détail d&#39;un article contenu dans une commande
*CommandesApi* | [**orders_order_id_cancel_post**](docs/CommandesApi.md#orders_order_id_cancel_post) | **POST** /orders/{orderId}/cancel | Annuler les paiements futurs pour une commande (pas de remboursement).
*CommandesApi* | [**orders_order_id_get**](docs/CommandesApi.md#orders_order_id_get) | **GET** /orders/{orderId} | Obtenir des informations détaillées sur une commande
*CommandesApi* | [**organizations_organization_slug_forms_form_type_form_slug_items_get**](docs/CommandesApi.md#organizations_organization_slug_forms_form_type_form_slug_items_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/items | Obtenir une liste d&#39;articles vendus dans un formulaire
*CommandesApi* | [**organizations_organization_slug_forms_form_type_form_slug_orders_get**](docs/CommandesApi.md#organizations_organization_slug_forms_form_type_form_slug_orders_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/orders | Obtenir les commandes d&#39;un formulaire
*CommandesApi* | [**organizations_organization_slug_items_get**](docs/CommandesApi.md#organizations_organization_slug_items_get) | **GET** /organizations/{organizationSlug}/items | Obtenir une liste d&#39;articles vendus par une organisation
*CommandesApi* | [**organizations_organization_slug_orders_get**](docs/CommandesApi.md#organizations_organization_slug_orders_get) | **GET** /organizations/{organizationSlug}/orders | Obtenir les commandes d&#39;une organisation
*FormulairesApi* | [**organizations_organization_slug_form_types_get**](docs/FormulairesApi.md#organizations_organization_slug_form_types_get) | **GET** /organizations/{organizationSlug}/formTypes | Obtenir une liste des types de formulaires pour une organisation
*FormulairesApi* | [**organizations_organization_slug_forms_form_type_action_quick_create_post**](docs/FormulairesApi.md#organizations_organization_slug_forms_form_type_action_quick_create_post) | **POST** /organizations/{organizationSlug}/forms/{formType}/action/quick-create | Créer un événement simplifié pour un organisme
*FormulairesApi* | [**organizations_organization_slug_forms_form_type_form_slug_public_get**](docs/FormulairesApi.md#organizations_organization_slug_forms_form_type_form_slug_public_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/public | Obtenir des données publiques détaillées sur un formulaire
*FormulairesApi* | [**organizations_organization_slug_forms_get**](docs/FormulairesApi.md#organizations_organization_slug_forms_get) | **GET** /organizations/{organizationSlug}/forms | Obtenir les formulaires d&#39;une organisation
*ListeDeValeursApi* | [**values_company_legal_status_get**](docs/ListeDeValeursApi.md#values_company_legal_status_get) | **GET** /values/company-legal-status | Obtenir la liste des statuts juridiques
*ListeDeValeursApi* | [**values_organization_categories_get**](docs/ListeDeValeursApi.md#values_organization_categories_get) | **GET** /values/organization/categories | Obtenir la liste des catégories du JO
*ListeDeValeursApi* | [**values_tags_get**](docs/ListeDeValeursApi.md#values_tags_get) | **GET** /values/tags | Obtenir la liste des tags publiques
*OrganisationApi* | [**organizations_legal_informations_legal_structures_get**](docs/OrganisationApi.md#organizations_legal_informations_legal_structures_get) | **GET** /organizations/legal-informations/legal-structures | Obtenir la structure juridique d&#39;une organisation visible.
*OrganisationApi* | [**organizations_legal_informations_organization_slug_configuration_get**](docs/OrganisationApi.md#organizations_legal_informations_organization_slug_configuration_get) | **GET** /organizations/legal-informations/{organizationSlug}/configuration | Obtenir la configuration des informations juridiques de l&#39;organisation.
*OrganisationApi* | [**organizations_legal_informations_organization_slug_configuration_put**](docs/OrganisationApi.md#organizations_legal_informations_organization_slug_configuration_put) | **PUT** /organizations/legal-informations/{organizationSlug}/configuration | Mettre à jour la configuration des informations juridiques de l&#39;organisation.
*OrganisationApi* | [**organizations_legal_informations_tax_information_texts_get**](docs/OrganisationApi.md#organizations_legal_informations_tax_information_texts_get) | **GET** /organizations/legal-informations/tax-information-texts | Obtenir les textes d&#39;information fiscale de l&#39;organisation.
*OrganisationApi* | [**organizations_organization_slug_get**](docs/OrganisationApi.md#organizations_organization_slug_get) | **GET** /organizations/{organizationSlug} | Obtenir le détail d&#39;une organisation
*PaiementsApi* | [**organizations_organization_slug_forms_form_type_form_slug_payments_get**](docs/PaiementsApi.md#organizations_organization_slug_forms_form_type_form_slug_payments_get) | **GET** /organizations/{organizationSlug}/forms/{formType}/{formSlug}/payments | Obtenir les informations des paiements effectués sur un formulaire
*PaiementsApi* | [**organizations_organization_slug_payments_get**](docs/PaiementsApi.md#organizations_organization_slug_payments_get) | **GET** /organizations/{organizationSlug}/payments | Obtenir les informations des paiements effectués sur une organisation
*PaiementsApi* | [**organizations_organization_slug_payments_search_get**](docs/PaiementsApi.md#organizations_organization_slug_payments_search_get) | **GET** /organizations/{organizationSlug}/payments/search | Rechercher des paiements.
*PaiementsApi* | [**payments_payment_id_get**](docs/PaiementsApi.md#payments_payment_id_get) | **GET** /payments/{paymentId} | Obtenir les informations détaillées d&#39;un paiement.
*PaiementsApi* | [**payments_payment_id_refund_post**](docs/PaiementsApi.md#payments_payment_id_refund_post) | **POST** /payments/{paymentId}/refund | Rembourser un paiement.
*PartenairesApi* | [**partners_me_api_clients_put**](docs/PartenairesApi.md#partners_me_api_clients_put) | **PUT** /partners/me/api-clients | Mise à jour du domaine
*PartenairesApi* | [**partners_me_api_notifications_delete**](docs/PartenairesApi.md#partners_me_api_notifications_delete) | **DELETE** /partners/me/api-notifications | Suppression de l&#39;URL de notification principale
*PartenairesApi* | [**partners_me_api_notifications_organizations_organization_slug_delete**](docs/PartenairesApi.md#partners_me_api_notifications_organizations_organization_slug_delete) | **DELETE** /partners/me/api-notifications/organizations/{organizationSlug} | Suppression d&#39;une URL de notification liée à une organisation
*PartenairesApi* | [**partners_me_api_notifications_organizations_organization_slug_put**](docs/PartenairesApi.md#partners_me_api_notifications_organizations_organization_slug_put) | **PUT** /partners/me/api-notifications/organizations/{organizationSlug} | Mise à jour d&#39;une URL de notification liée à une organisation
*PartenairesApi* | [**partners_me_api_notifications_put**](docs/PartenairesApi.md#partners_me_api_notifications_put) | **PUT** /partners/me/api-notifications | Mise à jour de l&#39;URL de notification principale
*PartenairesApi* | [**partners_me_get**](docs/PartenairesApi.md#partners_me_get) | **GET** /partners/me | Récupération des informations
*PartenairesApi* | [**partners_me_organizations_get**](docs/PartenairesApi.md#partners_me_organizations_get) | **GET** /partners/me/organizations | Obtenir toutes les organisations
*ReusFiscauxApi* | [**organizations_organization_slug_tax_receipt_configuration_get**](docs/ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_configuration_get) | **GET** /organizations/{organizationSlug}/tax-receipt/configuration | Obtenir la configuration des reçus fiscaux
*ReusFiscauxApi* | [**organizations_organization_slug_tax_receipt_configuration_put**](docs/ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_configuration_put) | **PUT** /organizations/{organizationSlug}/tax-receipt/configuration | Mettre à jour la configuration des reçus fiscaux
*ReusFiscauxApi* | [**organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put**](docs/ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_fiscal_receipt_transmitter_put) | **PUT** /organizations/{organizationSlug}/tax-receipt/fiscal-receipt-transmitter | Mettre à jour l&#39;émetteur des reçus fiscaux
*ReusFiscauxApi* | [**organizations_organization_slug_tax_receipt_preview_post**](docs/ReusFiscauxApi.md#organizations_organization_slug_tax_receipt_preview_post) | **POST** /organizations/{organizationSlug}/tax-receipt/preview | Prévisualiser les reçus fiscaux
*TagsApi* | [**tags_tag_name_get**](docs/TagsApi.md#tags_tag_name_get) | **GET** /tags/{tagName} | Obtenir le détail d&#39;un tag interne
*UtilisateursApi* | [**users_me_organizations_get**](docs/UtilisateursApi.md#users_me_organizations_get) | **GET** /users/me/organizations | Obtenir mes organisations


## Documentation For Models

 - [HaTrustContractLegalInformationAddressAddressDto](docs/HaTrustContractLegalInformationAddressAddressDto.md)
 - [HelloAssoApiV5ModelsAccountCompanyLegalStatusModel](docs/HelloAssoApiV5ModelsAccountCompanyLegalStatusModel.md)
 - [HelloAssoApiV5ModelsAccountOrganismCategoryModel](docs/HelloAssoApiV5ModelsAccountOrganismCategoryModel.md)
 - [HelloAssoApiV5ModelsAccountsClientsApiClientModel](docs/HelloAssoApiV5ModelsAccountsClientsApiClientModel.md)
 - [HelloAssoApiV5ModelsAccountsClientsPublicPutApiClientRequest](docs/HelloAssoApiV5ModelsAccountsClientsPublicPutApiClientRequest.md)
 - [HelloAssoApiV5ModelsApiNotificationsApiNotificationType](docs/HelloAssoApiV5ModelsApiNotificationsApiNotificationType.md)
 - [HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel](docs/HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel.md)
 - [HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody](docs/HelloAssoApiV5ModelsApiNotificationsPostApiUrlNotificationBody.md)
 - [HelloAssoApiV5ModelsCartsCheckoutIntentResponse](docs/HelloAssoApiV5ModelsCartsCheckoutIntentResponse.md)
 - [HelloAssoApiV5ModelsCartsCheckoutPayer](docs/HelloAssoApiV5ModelsCartsCheckoutPayer.md)
 - [HelloAssoApiV5ModelsCartsCheckoutTerm](docs/HelloAssoApiV5ModelsCartsCheckoutTerm.md)
 - [HelloAssoApiV5ModelsCartsInitCheckoutBody](docs/HelloAssoApiV5ModelsCartsInitCheckoutBody.md)
 - [HelloAssoApiV5ModelsCartsInitCheckoutResponse](docs/HelloAssoApiV5ModelsCartsInitCheckoutResponse.md)
 - [HelloAssoApiV5ModelsCommonContactModel](docs/HelloAssoApiV5ModelsCommonContactModel.md)
 - [HelloAssoApiV5ModelsCommonDocumentModel](docs/HelloAssoApiV5ModelsCommonDocumentModel.md)
 - [HelloAssoApiV5ModelsCommonMetaModel](docs/HelloAssoApiV5ModelsCommonMetaModel.md)
 - [HelloAssoApiV5ModelsCommonPaginationModel](docs/HelloAssoApiV5ModelsCommonPaginationModel.md)
 - [HelloAssoApiV5ModelsCommonPlaceModel](docs/HelloAssoApiV5ModelsCommonPlaceModel.md)
 - [HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel](docs/HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel.md)
 - [HelloAssoApiV5ModelsDirectoryListFormsRequest](docs/HelloAssoApiV5ModelsDirectoryListFormsRequest.md)
 - [HelloAssoApiV5ModelsDirectoryListOrganizationsRequest](docs/HelloAssoApiV5ModelsDirectoryListOrganizationsRequest.md)
 - [HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel](docs/HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel.md)
 - [HelloAssoApiV5ModelsDirectorySynchronizableFormModel](docs/HelloAssoApiV5ModelsDirectorySynchronizableFormModel.md)
 - [HelloAssoApiV5ModelsDirectorySynchronizableOrganizationModel](docs/HelloAssoApiV5ModelsDirectorySynchronizableOrganizationModel.md)
 - [HelloAssoApiV5ModelsEnumsFieldType](docs/HelloAssoApiV5ModelsEnumsFieldType.md)
 - [HelloAssoApiV5ModelsEnumsFormState](docs/HelloAssoApiV5ModelsEnumsFormState.md)
 - [HelloAssoApiV5ModelsEnumsFormType](docs/HelloAssoApiV5ModelsEnumsFormType.md)
 - [HelloAssoApiV5ModelsEnumsItemState](docs/HelloAssoApiV5ModelsEnumsItemState.md)
 - [HelloAssoApiV5ModelsEnumsMembershipValidityType](docs/HelloAssoApiV5ModelsEnumsMembershipValidityType.md)
 - [HelloAssoApiV5ModelsEnumsOperationState](docs/HelloAssoApiV5ModelsEnumsOperationState.md)
 - [HelloAssoApiV5ModelsEnumsOrganizationType](docs/HelloAssoApiV5ModelsEnumsOrganizationType.md)
 - [HelloAssoApiV5ModelsEnumsPaymentCashOutState](docs/HelloAssoApiV5ModelsEnumsPaymentCashOutState.md)
 - [HelloAssoApiV5ModelsEnumsPaymentFrequencyType](docs/HelloAssoApiV5ModelsEnumsPaymentFrequencyType.md)
 - [HelloAssoApiV5ModelsEnumsPaymentMeans](docs/HelloAssoApiV5ModelsEnumsPaymentMeans.md)
 - [HelloAssoApiV5ModelsEnumsPaymentProviderType](docs/HelloAssoApiV5ModelsEnumsPaymentProviderType.md)
 - [HelloAssoApiV5ModelsEnumsPaymentState](docs/HelloAssoApiV5ModelsEnumsPaymentState.md)
 - [HelloAssoApiV5ModelsEnumsPaymentType](docs/HelloAssoApiV5ModelsEnumsPaymentType.md)
 - [HelloAssoApiV5ModelsEnumsPriceCategory](docs/HelloAssoApiV5ModelsEnumsPriceCategory.md)
 - [HelloAssoApiV5ModelsEnumsRecordActionType](docs/HelloAssoApiV5ModelsEnumsRecordActionType.md)
 - [HelloAssoApiV5ModelsEnumsSortField](docs/HelloAssoApiV5ModelsEnumsSortField.md)
 - [HelloAssoApiV5ModelsEnumsSortOrder](docs/HelloAssoApiV5ModelsEnumsSortOrder.md)
 - [HelloAssoApiV5ModelsEnumsTagType](docs/HelloAssoApiV5ModelsEnumsTagType.md)
 - [HelloAssoApiV5ModelsEnumsTierType](docs/HelloAssoApiV5ModelsEnumsTierType.md)
 - [HelloAssoApiV5ModelsFormsFormBasicModel](docs/HelloAssoApiV5ModelsFormsFormBasicModel.md)
 - [HelloAssoApiV5ModelsFormsFormLightModel](docs/HelloAssoApiV5ModelsFormsFormLightModel.md)
 - [HelloAssoApiV5ModelsFormsFormPublicModel](docs/HelloAssoApiV5ModelsFormsFormPublicModel.md)
 - [HelloAssoApiV5ModelsFormsFormQuickCreateModel](docs/HelloAssoApiV5ModelsFormsFormQuickCreateModel.md)
 - [HelloAssoApiV5ModelsFormsFormQuickCreateRequest](docs/HelloAssoApiV5ModelsFormsFormQuickCreateRequest.md)
 - [HelloAssoApiV5ModelsFormsTermModel](docs/HelloAssoApiV5ModelsFormsTermModel.md)
 - [HelloAssoApiV5ModelsFormsTierLightModel](docs/HelloAssoApiV5ModelsFormsTierLightModel.md)
 - [HelloAssoApiV5ModelsFormsTierPublicModel](docs/HelloAssoApiV5ModelsFormsTierPublicModel.md)
 - [HelloAssoApiV5ModelsOrganizationLegalInformationsOrganizationLegalStructuresModel](docs/HelloAssoApiV5ModelsOrganizationLegalInformationsOrganizationLegalStructuresModel.md)
 - [HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationFiscalReceiptTransmitterBody](docs/HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationFiscalReceiptTransmitterBody.md)
 - [HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationLegalInformationConfigurationBody](docs/HelloAssoApiV5ModelsOrganizationLegalInformationsUpdateOrganizationLegalInformationConfigurationBody.md)
 - [HelloAssoApiV5ModelsOrganizationOrganizationBasicModel](docs/HelloAssoApiV5ModelsOrganizationOrganizationBasicModel.md)
 - [HelloAssoApiV5ModelsOrganizationOrganizationLightModel](docs/HelloAssoApiV5ModelsOrganizationOrganizationLightModel.md)
 - [HelloAssoApiV5ModelsOrganizationOrganizationModel](docs/HelloAssoApiV5ModelsOrganizationOrganizationModel.md)
 - [HelloAssoApiV5ModelsPartnerStatisticsModel](docs/HelloAssoApiV5ModelsPartnerStatisticsModel.md)
 - [HelloAssoApiV5ModelsPartnersPartnerPublicModel](docs/HelloAssoApiV5ModelsPartnersPartnerPublicModel.md)
 - [HelloAssoApiV5ModelsPaymentPublicPaymentModel](docs/HelloAssoApiV5ModelsPaymentPublicPaymentModel.md)
 - [HelloAssoApiV5ModelsPaymentRefundOperationModel](docs/HelloAssoApiV5ModelsPaymentRefundOperationModel.md)
 - [HelloAssoApiV5ModelsStatisticsItem](docs/HelloAssoApiV5ModelsStatisticsItem.md)
 - [HelloAssoApiV5ModelsStatisticsItemCustomField](docs/HelloAssoApiV5ModelsStatisticsItemCustomField.md)
 - [HelloAssoApiV5ModelsStatisticsItemDetail](docs/HelloAssoApiV5ModelsStatisticsItemDetail.md)
 - [HelloAssoApiV5ModelsStatisticsItemDiscount](docs/HelloAssoApiV5ModelsStatisticsItemDiscount.md)
 - [HelloAssoApiV5ModelsStatisticsItemOption](docs/HelloAssoApiV5ModelsStatisticsItemOption.md)
 - [HelloAssoApiV5ModelsStatisticsItemPayment](docs/HelloAssoApiV5ModelsStatisticsItemPayment.md)
 - [HelloAssoApiV5ModelsStatisticsOrder](docs/HelloAssoApiV5ModelsStatisticsOrder.md)
 - [HelloAssoApiV5ModelsStatisticsOrderAmountModel](docs/HelloAssoApiV5ModelsStatisticsOrderAmountModel.md)
 - [HelloAssoApiV5ModelsStatisticsOrderDetail](docs/HelloAssoApiV5ModelsStatisticsOrderDetail.md)
 - [HelloAssoApiV5ModelsStatisticsOrderItem](docs/HelloAssoApiV5ModelsStatisticsOrderItem.md)
 - [HelloAssoApiV5ModelsStatisticsOrderLight](docs/HelloAssoApiV5ModelsStatisticsOrderLight.md)
 - [HelloAssoApiV5ModelsStatisticsOrderPayment](docs/HelloAssoApiV5ModelsStatisticsOrderPayment.md)
 - [HelloAssoApiV5ModelsStatisticsPayer](docs/HelloAssoApiV5ModelsStatisticsPayer.md)
 - [HelloAssoApiV5ModelsStatisticsPayment](docs/HelloAssoApiV5ModelsStatisticsPayment.md)
 - [HelloAssoApiV5ModelsStatisticsPaymentDetail](docs/HelloAssoApiV5ModelsStatisticsPaymentDetail.md)
 - [HelloAssoApiV5ModelsStatisticsPaymentItem](docs/HelloAssoApiV5ModelsStatisticsPaymentItem.md)
 - [HelloAssoApiV5ModelsStatisticsRefundOperationLightModel](docs/HelloAssoApiV5ModelsStatisticsRefundOperationLightModel.md)
 - [HelloAssoApiV5ModelsStatisticsShareItem](docs/HelloAssoApiV5ModelsStatisticsShareItem.md)
 - [HelloAssoApiV5ModelsStatisticsSharePayment](docs/HelloAssoApiV5ModelsStatisticsSharePayment.md)
 - [HelloAssoApiV5ModelsStatisticsUser](docs/HelloAssoApiV5ModelsStatisticsUser.md)
 - [HelloAssoApiV5ModelsTagsInternalTagModel](docs/HelloAssoApiV5ModelsTagsInternalTagModel.md)
 - [HelloAssoApiV5ModelsTagsPublicTagModel](docs/HelloAssoApiV5ModelsTagsPublicTagModel.md)
 - [HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration](docs/HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration.md)
 - [HelloAssoModelsAccountsOrganizationLegalInformationsFiscalReceiptSignatoryModel](docs/HelloAssoModelsAccountsOrganizationLegalInformationsFiscalReceiptSignatoryModel.md)
 - [HelloAssoModelsAccountsOrganizationLegalInformationsOrganizationLegalInformationConfiguration](docs/HelloAssoModelsAccountsOrganizationLegalInformationsOrganizationLegalInformationConfiguration.md)
 - [HelloAssoModelsAccountsOrganizationLegalInformationsTaxInformationText](docs/HelloAssoModelsAccountsOrganizationLegalInformationsTaxInformationText.md)
 - [HelloAssoModelsEnumsGlobalRole](docs/HelloAssoModelsEnumsGlobalRole.md)
 - [HelloAssoModelsPaymentsCashInFiscalReceiptFiscalReceiptFormatOption](docs/HelloAssoModelsPaymentsCashInFiscalReceiptFiscalReceiptFormatOption.md)
 - [HelloAssoModelsSharedGeoLocation](docs/HelloAssoModelsSharedGeoLocation.md)
 - [ResultsWithPaginationModelFormLightModel](docs/ResultsWithPaginationModelFormLightModel.md)
 - [ResultsWithPaginationModelItem](docs/ResultsWithPaginationModelItem.md)
 - [ResultsWithPaginationModelOrder](docs/ResultsWithPaginationModelOrder.md)
 - [ResultsWithPaginationModelPartnerOrganizationModel](docs/ResultsWithPaginationModelPartnerOrganizationModel.md)
 - [ResultsWithPaginationModelPayment](docs/ResultsWithPaginationModelPayment.md)
 - [ResultsWithPaginationModelPublicPaymentModel](docs/ResultsWithPaginationModelPublicPaymentModel.md)
 - [ResultsWithPaginationModelSynchronizableFormModel](docs/ResultsWithPaginationModelSynchronizableFormModel.md)
 - [ResultsWithPaginationModelSynchronizableOrganizationModel](docs/ResultsWithPaginationModelSynchronizableOrganizationModel.md)


## Authorization

We use OAuth2 for authentication, so to avoid reinventing the wheel, we recommend using the [Authlib](https://pypi.org/project/Authlib) package

### Prerequisite
Install the Authlib package:

```bash
pip install requests
pip install Authlib
```

### Client Credentials Flow
```python
from authlib.integrations.requests_client import OAuth2Session

# Configuration
client_id = 'your_client_id'
client_secret = 'your_client_secret'
token_url = 'https://api.helloasso.com/oauth2/token'

# Create an OAuth2 session
client = OAuth2Session(client_id, client_secret)

# Get an access token
def get_access_token():
    token = client.fetch_token(token_url, grant_type='client_credentials')
    print("Access Token:", token['access_token'])
    print("Expires In:", token['expires_in'])
    print("Refresh Token:", token['refresh_token'])
    return token

# Usage
get_access_token()
```

### Refresh Token Flow
```python
from authlib.integrations.requests_client import OAuth2Session

# Configuration
client_id = 'your_client_id'
client_secret = 'your_client_secret'
token_url = 'https://api.helloasso.com/oauth2/token'

# Refresh the token
def refresh_access_token(refresh_token):
    client = OAuth2Session(client_id, client_secret)
    token = client.refresh_token(token_url, refresh_token=refresh_token)
    print("New Access Token:", token['access_token'])
    print("Expires In:", token['expires_in'])
    print("New Refresh Token:", token['refresh_token'])
    return token

# Usage
refresh_access_token('your_refresh_token')
```

### Authorization Code Flow
```python
import base64
import hashlib
import os
from authlib.integrations.requests_client import OAuth2Session

# Configuration
client_id = 'your_client_id'
client_secret = 'your_client_secret'
authorize_url = 'https://auth.helloasso.com/authorize'
token_url = 'https://api.helloasso.com/oauth2/token'
redirect_uri = 'https://your-app.com/callback'

# PKCE Helper Functions
def generate_code_verifier():
    """Generate a high-entropy code_verifier."""
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')

def generate_code_challenge(code_verifier):
    """Generate a code_challenge based on the code_verifier."""
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('utf-8')

# Step 1: Generate the Authorization URL
def get_authorization_url():
    # Generate PKCE parameters
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    client = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
    authorization_url, state = client.create_authorization_url(authorize_url, code_challenge=code_challenge, code_challenge_method='S256')
    print("Authorization URL: ", authorization_url)
    print("Code verifier: ", code_verifier)

# Step 2: Exchange the authorization code for an access token
def get_access_token_from_code(authorization_response, code_verifier):
    client = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
    token = client.fetch_token(token_url, authorization_response=authorization_response, code_verifier=code_verifier)
    print("Access Token: ", token['access_token'])
    print("Expires In: ", token['expires_in'])
    print("Refresh Token: ", token['refresh_token'])

# Usage
get_authorization_url()
# After user authorizes, exchange the code (passed in the redirect URL callback)
#get_access_token_from_code('your_authorization_code', 'your_code_verifier')
```

## About this package

This SDK is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- Generator version: 7.10.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen
