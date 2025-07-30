# HelloAssoApiV5ModelsFormsFormQuickCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tier_list** | [**List[HelloAssoApiV5ModelsFormsTierLightModel]**](HelloAssoApiV5ModelsFormsTierLightModel.md) |  | [optional] 
**banner** | **str** | The banner of the form | [optional] 
**description** | **str** | The description of form | [optional] 
**end_date** | **datetime** | The datetime of the activity end | [optional] 
**logo** | **str** | The logo of the form | [optional] 
**private_title** | **str** | Private Title : displayed only in the organization back office | [optional] 
**start_date** | **datetime** | The datetime of the activity start | [optional] 
**title** | **str** | The title of the form. It will be used to generate the url which that can&#39;t be changed. | 
**activity_type_id** | **int** | Activity type identifier, matching one of the provided type values &lt;a href&#x3D;\&quot;index#!/Values/Values_Get\&quot;&gt; provided here&lt;/a&gt; | [optional] 
**place** | [**HelloAssoApiV5ModelsCommonPlaceModel**](HelloAssoApiV5ModelsCommonPlaceModel.md) |  | [optional] 
**sale_end_date** | **datetime** | The datetime (Inclusive) at which the sales end.  If null the orders will be available until the end of the campaign. | [optional] 
**sale_start_date** | **datetime** | The datetime (Inclusive) at which the users can start placing orders.  If null the orders will be available as soon as the campaign is published. | [optional] 
**validity_type** | [**HelloAssoApiV5ModelsEnumsMembershipValidityType**](HelloAssoApiV5ModelsEnumsMembershipValidityType.md) |  | [optional] 
**accept_open_donation** | **bool** | Whether the user will be allowed to make a single open donation with an order. The amount of the donation is open, but 3 presets can be set in OpenDonationPresetAmount | [optional] 
**accept_open_monthly_donation** | **bool** | Whether the user will be allowed to make a monthly open donation for donation forms | [optional] 
**allow_comment** | **bool** | allowComment | [optional] 
**amount_visible** | **bool** | amountVisible | [optional] 
**color** | **str** | The color of the form | [optional] 
**widget_button_text** | **str** | The text displayed in the widget button | [optional] 
**contact** | [**HelloAssoApiV5ModelsCommonContactModel**](HelloAssoApiV5ModelsCommonContactModel.md) |  | [optional] 
**display_contributor_name** | **bool** | Display contributor name for fundraiser | [optional] 
**display_participants_count** | **bool** | Indicates that the members count must be displayed on the form. | [optional] 
**display_remaining_entries** | **bool** | Indicates that the remaining entries must be displayed on the form. | [optional] 
**financial_goal** | **int** | Indicates the financial goal (amount of money raised) for the whole form. Null means no goal. | [optional] 
**generate_membership_cards** | **bool** | Entrust the issuance of membership cards to HelloAsso (automatically sent by email to participants) | [optional] 
**generate_tickets** | **bool** | Entrust the issuance of tickets to HelloAsso (automatically sent by email to participants) | [optional] 
**invert_descriptions** | **bool** | Allows you to add the long description above the store catalog. | [optional] 
**label_conditions_and_terms_file** | **str** | Label conditions and terms file | [optional] 
**long_description** | **str** | The long description of the form (rich Html) | [optional] 
**open_donation_preset_amounts** | **List[int]** | The preset amounts to be shown to the user. Maximum 3 amounts. | [optional] 
**personalized_message** | **str** | Personalized message for participants | [optional] 
**project_beneficiaries** | **str** | The project beneficiaries of the form (rich Html) | [optional] 
**project_expenses_details** | **str** | Details of the project expenses (rich Html) | [optional] 
**project_owners** | **str** | Description of the project owners (rich Html) | [optional] 
**project_target_country** | **str** | 3 letter country code | [optional] 
**allow_organism_payer** | **bool** | Whether users are allowed to contribute to this form through an organism (only for donation and crowdfunding). | [optional] 
**allow_individual_payer** | **bool** | Whether user are allowed to personally contribute to this form (only for donation and crowdfunding). | [optional] 
**display_version** | **int** | The form display version (only for donation). | [optional] 
**max_entries** | **int** | Indicates the maximum available entries for the whole form. Null means unlimited entries. | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_forms_form_quick_create_request import HelloAssoApiV5ModelsFormsFormQuickCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsFormsFormQuickCreateRequest from a JSON string
hello_asso_api_v5_models_forms_form_quick_create_request_instance = HelloAssoApiV5ModelsFormsFormQuickCreateRequest.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsFormsFormQuickCreateRequest.to_json())

# convert the object into a dict
hello_asso_api_v5_models_forms_form_quick_create_request_dict = hello_asso_api_v5_models_forms_form_quick_create_request_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsFormsFormQuickCreateRequest from a dict
hello_asso_api_v5_models_forms_form_quick_create_request_from_dict = HelloAssoApiV5ModelsFormsFormQuickCreateRequest.from_dict(hello_asso_api_v5_models_forms_form_quick_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


