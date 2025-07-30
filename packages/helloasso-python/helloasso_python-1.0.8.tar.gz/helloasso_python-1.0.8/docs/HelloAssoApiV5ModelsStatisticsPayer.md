# HelloAssoApiV5ModelsStatisticsPayer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | [optional] 
**address** | **str** | Gets or Sets Address | [optional] 
**city** | **str** | Gets or Sets City | [optional] 
**zip_code** | **str** | Gets or Sets ZipCode | [optional] 
**country** | **str** | Gets or Sets Country | [optional] 
**company** | **str** | Gets or Sets Company | [optional] 
**date_of_birth** | **datetime** | Gets or Sets date of birth | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_payer import HelloAssoApiV5ModelsStatisticsPayer

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsPayer from a JSON string
hello_asso_api_v5_models_statistics_payer_instance = HelloAssoApiV5ModelsStatisticsPayer.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsPayer.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_payer_dict = hello_asso_api_v5_models_statistics_payer_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsPayer from a dict
hello_asso_api_v5_models_statistics_payer_from_dict = HelloAssoApiV5ModelsStatisticsPayer.from_dict(hello_asso_api_v5_models_statistics_payer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


