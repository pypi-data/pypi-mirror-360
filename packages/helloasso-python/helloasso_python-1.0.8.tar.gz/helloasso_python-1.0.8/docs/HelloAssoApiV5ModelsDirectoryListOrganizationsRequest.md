# HelloAssoApiV5ModelsDirectoryListOrganizationsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Textual search for organization name | [optional] 
**description** | **str** | Textual search for organization description | [optional] 
**categories** | **List[str]** | The categories of the organizations | [optional] 
**types** | **List[str]** | The organization types | [optional] 
**zip_codes** | **List[str]** | The zip codes where the organizations are located | [optional] 
**cities** | **List[str]** | The cities where the organizations are located | [optional] 
**regions** | **List[str]** | The regions where the organizations are located | [optional] 
**departments** | **List[str]** | The departments where the organizations are located | [optional] 
**fiscal_receipt_eligibility** | **bool** | Allow only organization with a fiscal receipt eligibility | [optional] 
**internal_tags** | **List[str]** | Allow only Organization with internal tags  this filter is for special operations only | [optional] 
**tags** | **List[str]** | Allow only Organization with public tags | [optional] 
**linked_partners** | **List[str]** | Allow only Organization with linked partners | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_directory_list_organizations_request import HelloAssoApiV5ModelsDirectoryListOrganizationsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsDirectoryListOrganizationsRequest from a JSON string
hello_asso_api_v5_models_directory_list_organizations_request_instance = HelloAssoApiV5ModelsDirectoryListOrganizationsRequest.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsDirectoryListOrganizationsRequest.to_json())

# convert the object into a dict
hello_asso_api_v5_models_directory_list_organizations_request_dict = hello_asso_api_v5_models_directory_list_organizations_request_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsDirectoryListOrganizationsRequest from a dict
hello_asso_api_v5_models_directory_list_organizations_request_from_dict = HelloAssoApiV5ModelsDirectoryListOrganizationsRequest.from_dict(hello_asso_api_v5_models_directory_list_organizations_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


