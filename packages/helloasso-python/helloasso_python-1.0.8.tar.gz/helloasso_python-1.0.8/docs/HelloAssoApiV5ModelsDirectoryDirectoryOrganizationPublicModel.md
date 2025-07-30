# HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel

DirectoryOrganizationPublicModel class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tags** | **List[str]** | The public tags of the organization | [optional] 
**linked_partners** | **List[str]** | Partners linked to this organization | [optional] 
**is_authenticated** | **bool** | The organization is authenticated. Property returned only when asked by an organization admin. | [optional] 
**is_cash_in_compliant** | **bool** | If transaction can be init on the organization or not. | [optional] 
**banner** | **str** | The organization banner | [optional] 
**fiscal_receipt_eligibility** | **bool** | The organism can issue fiscal receipts (type ok and has not deactivated it)  Must configure it and be authenticated to become enabled | [optional] 
**fiscal_receipt_issuance_enabled** | **bool** | The organism is eligible, has set up his options, and is authenticated. | [optional] 
**type** | [**HelloAssoApiV5ModelsEnumsOrganizationType**](HelloAssoApiV5ModelsEnumsOrganizationType.md) |  | [optional] 
**category** | **str** | Organization category label | [optional] 
**address** | **str** | Organization Address (for authorized applications or if authorized by the organization) | [optional] 
**geolocation** | [**HelloAssoModelsSharedGeoLocation**](HelloAssoModelsSharedGeoLocation.md) |  | [optional] 
**rna_number** | **str** | Unique identifier assigned when creating the association | [optional] 
**logo** | **str** | Logo of organization | [optional] 
**name** | **str** | Name of organization | [optional] 
**role** | [**HelloAssoModelsEnumsGlobalRole**](HelloAssoModelsEnumsGlobalRole.md) |  | [optional] 
**city** | **str** | Organization city | [optional] 
**zip_code** | **str** | Organization zip code | [optional] 
**description** | **str** | Organization description | [optional] 
**update_date** | **datetime** | Last update date of the organization | [optional] 
**category_jo_id** | **int** |  | [optional] 
**url** | **str** | The organization url | [optional] 
**organization_slug** | **str** | The organization slug | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_directory_directory_organization_public_model import HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel from a JSON string
hello_asso_api_v5_models_directory_directory_organization_public_model_instance = HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_directory_directory_organization_public_model_dict = hello_asso_api_v5_models_directory_directory_organization_public_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel from a dict
hello_asso_api_v5_models_directory_directory_organization_public_model_from_dict = HelloAssoApiV5ModelsDirectoryDirectoryOrganizationPublicModel.from_dict(hello_asso_api_v5_models_directory_directory_organization_public_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


