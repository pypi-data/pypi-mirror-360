# HelloAssoApiV5ModelsStatisticsItemOption

ItemOption class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the option | [optional] 
**amount** | **int** | Amount of the option in cents | [optional] 
**price_category** | [**HelloAssoApiV5ModelsEnumsPriceCategory**](HelloAssoApiV5ModelsEnumsPriceCategory.md) |  | [optional] 
**is_required** | **bool** | Option is required or optional | [optional] 
**custom_fields** | [**List[HelloAssoApiV5ModelsStatisticsItemCustomField]**](HelloAssoApiV5ModelsStatisticsItemCustomField.md) | Custom fields related to this option | [optional] 
**option_id** | **int** |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_item_option import HelloAssoApiV5ModelsStatisticsItemOption

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsItemOption from a JSON string
hello_asso_api_v5_models_statistics_item_option_instance = HelloAssoApiV5ModelsStatisticsItemOption.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsItemOption.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_item_option_dict = hello_asso_api_v5_models_statistics_item_option_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsItemOption from a dict
hello_asso_api_v5_models_statistics_item_option_from_dict = HelloAssoApiV5ModelsStatisticsItemOption.from_dict(hello_asso_api_v5_models_statistics_item_option_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


