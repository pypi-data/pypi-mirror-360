# HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel

PartnerOrganizationModel class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization** | [**HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel**](HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel.md) |  | [optional] 
**available_access_token** | **bool** | True if exist a valid organization access token obtained by authorize flow | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_directory_partner_organization_model import HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel from a JSON string
hello_asso_api_v5_models_directory_partner_organization_model_instance = HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_directory_partner_organization_model_dict = hello_asso_api_v5_models_directory_partner_organization_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel from a dict
hello_asso_api_v5_models_directory_partner_organization_model_from_dict = HelloAssoApiV5ModelsDirectoryPartnerOrganizationModel.from_dict(hello_asso_api_v5_models_directory_partner_organization_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


