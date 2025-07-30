# HelloAssoApiV5ModelsAccountsClientsApiClientModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**secret** | **str** | Filled only when requested by the organization back office | [optional] 
**partner_name** | **str** |  | [optional] 
**privileges** | **List[str]** |  | [optional] 
**domain** | **str** |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_accounts_clients_api_client_model import HelloAssoApiV5ModelsAccountsClientsApiClientModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsAccountsClientsApiClientModel from a JSON string
hello_asso_api_v5_models_accounts_clients_api_client_model_instance = HelloAssoApiV5ModelsAccountsClientsApiClientModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsAccountsClientsApiClientModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_accounts_clients_api_client_model_dict = hello_asso_api_v5_models_accounts_clients_api_client_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsAccountsClientsApiClientModel from a dict
hello_asso_api_v5_models_accounts_clients_api_client_model_from_dict = HelloAssoApiV5ModelsAccountsClientsApiClientModel.from_dict(hello_asso_api_v5_models_accounts_clients_api_client_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


