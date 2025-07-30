# HelloAssoApiV5ModelsPartnersPartnerPublicModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the partner | [optional] 
**display_name** | **str** | Display Name of the partner | [optional] 
**description** | **str** | Description of the partner | [optional] 
**url** | **str** | Website of the partner | [optional] 
**logo** | **str** | Logo of the partner : square format | [optional] 
**logo_rectangle** | **str** | Logo of the partner : rectangle format | [optional] 
**api_client** | [**HelloAssoApiV5ModelsAccountsClientsApiClientModel**](HelloAssoApiV5ModelsAccountsClientsApiClientModel.md) |  | [optional] 
**url_notification_list** | [**List[HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel]**](HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel.md) | Url Notification of the partner | [optional] 
**partner_statistics** | [**HelloAssoApiV5ModelsPartnerStatisticsModel**](HelloAssoApiV5ModelsPartnerStatisticsModel.md) |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_partners_partner_public_model import HelloAssoApiV5ModelsPartnersPartnerPublicModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsPartnersPartnerPublicModel from a JSON string
hello_asso_api_v5_models_partners_partner_public_model_instance = HelloAssoApiV5ModelsPartnersPartnerPublicModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsPartnersPartnerPublicModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_partners_partner_public_model_dict = hello_asso_api_v5_models_partners_partner_public_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsPartnersPartnerPublicModel from a dict
hello_asso_api_v5_models_partners_partner_public_model_from_dict = HelloAssoApiV5ModelsPartnersPartnerPublicModel.from_dict(hello_asso_api_v5_models_partners_partner_public_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


