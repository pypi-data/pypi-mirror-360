# HelloAssoApiV5ModelsStatisticsPaymentItem

Item linked to a payment

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**share_amount** | **int** | Amount of the payment assigned to the item and its options (in cents) | [optional] 
**share_item_amount** | **int** | Amount of the item payed on this payment term (in cents) | [optional] 
**share_options_amount** | **int** | Amount of all extra options linked to this item and payed on this payment (in cents) | [optional] 
**id** | **int** | ID of the Item | [optional] 
**amount** | **int** | Total item Price in cents (after discount without extra options) | [optional] 
**type** | [**HelloAssoApiV5ModelsEnumsTierType**](HelloAssoApiV5ModelsEnumsTierType.md) |  | [optional] 
**initial_amount** | **int** | The raw amount (without reduction) | [optional] 
**state** | [**HelloAssoApiV5ModelsEnumsItemState**](HelloAssoApiV5ModelsEnumsItemState.md) |  | [optional] 
**name** | **str** | Name of the item paid (relevant for checkout forms) | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_payment_item import HelloAssoApiV5ModelsStatisticsPaymentItem

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsPaymentItem from a JSON string
hello_asso_api_v5_models_statistics_payment_item_instance = HelloAssoApiV5ModelsStatisticsPaymentItem.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsPaymentItem.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_payment_item_dict = hello_asso_api_v5_models_statistics_payment_item_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsPaymentItem from a dict
hello_asso_api_v5_models_statistics_payment_item_from_dict = HelloAssoApiV5ModelsStatisticsPaymentItem.from_dict(hello_asso_api_v5_models_statistics_payment_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


