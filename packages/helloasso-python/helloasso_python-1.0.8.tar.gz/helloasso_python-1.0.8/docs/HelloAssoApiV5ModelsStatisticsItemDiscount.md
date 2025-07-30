# HelloAssoApiV5ModelsStatisticsItemDiscount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The discount code applied on the item | [optional] 
**amount** | **int** | The discount amount in cents | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_item_discount import HelloAssoApiV5ModelsStatisticsItemDiscount

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsItemDiscount from a JSON string
hello_asso_api_v5_models_statistics_item_discount_instance = HelloAssoApiV5ModelsStatisticsItemDiscount.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsItemDiscount.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_item_discount_dict = hello_asso_api_v5_models_statistics_item_discount_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsItemDiscount from a dict
hello_asso_api_v5_models_statistics_item_discount_from_dict = HelloAssoApiV5ModelsStatisticsItemDiscount.from_dict(hello_asso_api_v5_models_statistics_item_discount_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


