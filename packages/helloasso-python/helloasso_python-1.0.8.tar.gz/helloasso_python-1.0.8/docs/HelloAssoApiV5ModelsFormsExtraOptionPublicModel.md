# HelloAssoApiV5ModelsFormsExtraOptionPublicModel

ExtraOptionFullModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | [**List[HelloAssoApiV5ModelsFormsCustomFieldPublicModel]**](HelloAssoApiV5ModelsFormsCustomFieldPublicModel.md) | List of custom fields to be filled by the user | [optional] 
**id** | **int** | Id | [optional] 
**price** | **int** | Price of the extraOption, can be free | [optional] 
**vat_rate** | **float** | Vat rate if applicable  Amount have to be 0.10 for 10% | [optional] 
**label** | **str** | The name of the option | [optional] 
**description** | **str** | The description of the option | [optional] 
**is_required** | **bool** | Additional option is required/mandatory | [optional] [readonly] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_forms_extra_option_public_model import HelloAssoApiV5ModelsFormsExtraOptionPublicModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsFormsExtraOptionPublicModel from a JSON string
hello_asso_api_v5_models_forms_extra_option_public_model_instance = HelloAssoApiV5ModelsFormsExtraOptionPublicModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsFormsExtraOptionPublicModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_forms_extra_option_public_model_dict = hello_asso_api_v5_models_forms_extra_option_public_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsFormsExtraOptionPublicModel from a dict
hello_asso_api_v5_models_forms_extra_option_public_model_from_dict = HelloAssoApiV5ModelsFormsExtraOptionPublicModel.from_dict(hello_asso_api_v5_models_forms_extra_option_public_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


