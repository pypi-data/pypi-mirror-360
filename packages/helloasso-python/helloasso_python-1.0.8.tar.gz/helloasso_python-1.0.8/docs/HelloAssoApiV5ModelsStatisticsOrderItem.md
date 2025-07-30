# HelloAssoApiV5ModelsStatisticsOrderItem

Item on the order

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payments** | [**List[HelloAssoApiV5ModelsStatisticsSharePayment]**](HelloAssoApiV5ModelsStatisticsSharePayment.md) | Payments linked to this item and each share between the item and the payment | [optional] 
**name** | **str** |  | [optional] 
**user** | [**HelloAssoApiV5ModelsStatisticsUser**](HelloAssoApiV5ModelsStatisticsUser.md) |  | [optional] 
**price_category** | [**HelloAssoApiV5ModelsEnumsPriceCategory**](HelloAssoApiV5ModelsEnumsPriceCategory.md) |  | [optional] 
**min_amount** | **int** | Minimum amount that was specified on the tier (in cents) | [optional] 
**discount** | [**HelloAssoApiV5ModelsStatisticsItemDiscount**](HelloAssoApiV5ModelsStatisticsItemDiscount.md) |  | [optional] 
**custom_fields** | [**List[HelloAssoApiV5ModelsStatisticsItemCustomField]**](HelloAssoApiV5ModelsStatisticsItemCustomField.md) | Custom fields related to this item | [optional] 
**options** | [**List[HelloAssoApiV5ModelsStatisticsItemOption]**](HelloAssoApiV5ModelsStatisticsItemOption.md) | Extra options taken with this item | [optional] 
**ticket_url** | **str** | The Ticket Url | [optional] 
**qr_code** | **str** | The item QrCode (for ticket scanning only) | [optional] 
**membership_card_url** | **str** | The Membership Card Url | [optional] 
**day_of_levy** | **int** | The day of levy for monthly donation only | [optional] 
**tier_description** | **str** | Tier description | [optional] 
**tier_id** | **int** |  | [optional] 
**comment** | **str** |  | [optional] 
**id** | **int** | ID of the Item | [optional] 
**amount** | **int** | Total item Price in cents (after discount without extra options) | [optional] 
**type** | [**HelloAssoApiV5ModelsEnumsTierType**](HelloAssoApiV5ModelsEnumsTierType.md) |  | [optional] 
**initial_amount** | **int** | The raw amount (without reduction) | [optional] 
**state** | [**HelloAssoApiV5ModelsEnumsItemState**](HelloAssoApiV5ModelsEnumsItemState.md) |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_order_item import HelloAssoApiV5ModelsStatisticsOrderItem

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsOrderItem from a JSON string
hello_asso_api_v5_models_statistics_order_item_instance = HelloAssoApiV5ModelsStatisticsOrderItem.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsOrderItem.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_order_item_dict = hello_asso_api_v5_models_statistics_order_item_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsOrderItem from a dict
hello_asso_api_v5_models_statistics_order_item_from_dict = HelloAssoApiV5ModelsStatisticsOrderItem.from_dict(hello_asso_api_v5_models_statistics_order_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


