# HelloAssoApiV5ModelsCommonContactModel

Contact class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | Contact email | [optional] 
**phone_number** | **str** | Contact phone number | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_common_contact_model import HelloAssoApiV5ModelsCommonContactModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsCommonContactModel from a JSON string
hello_asso_api_v5_models_common_contact_model_instance = HelloAssoApiV5ModelsCommonContactModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsCommonContactModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_common_contact_model_dict = hello_asso_api_v5_models_common_contact_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsCommonContactModel from a dict
hello_asso_api_v5_models_common_contact_model_from_dict = HelloAssoApiV5ModelsCommonContactModel.from_dict(hello_asso_api_v5_models_common_contact_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


