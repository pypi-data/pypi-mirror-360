# HelloAssoApiV5ModelsPartnerStatisticsModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**linked_organizations_count** | **int** | Number of organizations linked to this partner | [optional] 
**linked_organizations_collected_amount** | **int** | Collected amount by linked organizations | [optional] 
**checkout_collected_amount** | **int** | Collected amount by All partner checkouts | [optional] 
**organizations_using_checkout** | **int** | Number of organizations using the checkout with this partner | [optional] 
**available_organizations_access_token_count** | **int** | Number of organizations access token obtains by authorize flow | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_partner_statistics_model import HelloAssoApiV5ModelsPartnerStatisticsModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsPartnerStatisticsModel from a JSON string
hello_asso_api_v5_models_partner_statistics_model_instance = HelloAssoApiV5ModelsPartnerStatisticsModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsPartnerStatisticsModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_partner_statistics_model_dict = hello_asso_api_v5_models_partner_statistics_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsPartnerStatisticsModel from a dict
hello_asso_api_v5_models_partner_statistics_model_from_dict = HelloAssoApiV5ModelsPartnerStatisticsModel.from_dict(hello_asso_api_v5_models_partner_statistics_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


