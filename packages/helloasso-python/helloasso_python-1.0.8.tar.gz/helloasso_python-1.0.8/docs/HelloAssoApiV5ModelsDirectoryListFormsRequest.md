# HelloAssoApiV5ModelsDirectoryListFormsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**form_name** | **str** | Textual search for form name | [optional] 
**form_description** | **str** | Textual search for form description | [optional] 
**form_zip_codes** | **List[str]** | The zip codes where the forms are located | [optional] 
**form_cities** | **List[str]** | The cities where the forms are located | [optional] 
**form_regions** | **List[str]** | The regions where the forms are located | [optional] 
**form_departments** | **List[str]** | The departments where the forms are located | [optional] 
**form_countries** | **List[str]** | The countries where the forms are located | [optional] 
**form_types** | [**List[HelloAssoApiV5ModelsEnumsFormType]**](HelloAssoApiV5ModelsEnumsFormType.md) | The form types : CrowdFunding, Membership, Event, Donation, PaymentForm ... | [optional] 
**form_activity_type** | **List[str]** | The Activity Type of the form | [optional] 
**form_publication_start_date_min** | **datetime** | The inclusive minimum publication date of the forms, format \&quot;yyyy-MM-ddTHH:mm:ss.fffK\&quot; | [optional] 
**form_publication_start_date_max** | **datetime** | The exclusive maximum publication date of the forms, format \&quot;yyyy-MM-ddTHH:mm:ss.fffK\&quot; | [optional] 
**form_start_date_min** | **datetime** | The inclusive minimum start date of the forms, format \&quot;yyyy-MM-ddTHH:mm:ss.fffK\&quot; | [optional] 
**form_start_date_max** | **datetime** | The exclusive maximum start date of the forms, format \&quot;yyyy-MM-ddTHH:mm:ss.fffK\&quot; | [optional] 
**form_end_date_max** | **datetime** | The exclusive maximum end date of the forms, format \&quot;yyyy-MM-ddTHH:mm:ss.fffK\&quot; | [optional] 
**form_end_date_min** | **datetime** | The inclusive minimum end date of the forms, format \&quot;yyyy-MM-ddTHH:mm:ss.fffK\&quot; | [optional] 
**form_is_free** | **bool** | Allow only free forms if true | [optional] 
**form_has_remaining_entries** | **bool** | Allow only forms with remaning entries if true | [optional] 
**form_internal_tags** | **List[str]** | Allow only forms with internal tags  this filter is for special operations only | [optional] 
**form_public_tags** | **List[str]** | Allow only forms with public tags | [optional] 
**organization_name** | **str** | Textual search for organization name | [optional] 
**organization_description** | **str** | Textual search for organization description | [optional] 
**organization_categories** | **List[str]** | The categories of the forms | [optional] 
**organization_types** | **List[str]** | The organization types | [optional] 
**organization_zip_codes** | **List[str]** | The zip codes where the organizations are located | [optional] 
**organization_cities** | **List[str]** | The cities where the organizations are located | [optional] 
**organization_regions** | **List[str]** | The regions where the organizations are located | [optional] 
**organization_departments** | **List[str]** | The departments where the organizations are located | [optional] 
**organization_fiscal_receipt_eligibility** | **bool** | Allow only organization with a fiscal receipt eligibility | [optional] 
**organization_linked_partners** | **List[str]** | Organization linked partners | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_directory_list_forms_request import HelloAssoApiV5ModelsDirectoryListFormsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsDirectoryListFormsRequest from a JSON string
hello_asso_api_v5_models_directory_list_forms_request_instance = HelloAssoApiV5ModelsDirectoryListFormsRequest.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsDirectoryListFormsRequest.to_json())

# convert the object into a dict
hello_asso_api_v5_models_directory_list_forms_request_dict = hello_asso_api_v5_models_directory_list_forms_request_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsDirectoryListFormsRequest from a dict
hello_asso_api_v5_models_directory_list_forms_request_from_dict = HelloAssoApiV5ModelsDirectoryListFormsRequest.from_dict(hello_asso_api_v5_models_directory_list_forms_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


