# HelloAssoApiV5ModelsStatisticsItemDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order** | [**HelloAssoApiV5ModelsStatisticsOrderLight**](HelloAssoApiV5ModelsStatisticsOrderLight.md) |  | [optional] 
**payer** | [**HelloAssoApiV5ModelsStatisticsPayer**](HelloAssoApiV5ModelsStatisticsPayer.md) |  | [optional] 
**payments** | [**List[HelloAssoApiV5ModelsStatisticsItemPayment]**](HelloAssoApiV5ModelsStatisticsItemPayment.md) | Payments linked to this item | [optional] 
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
from helloasso_python.models.hello_asso_api_v5_models_statistics_item_detail import HelloAssoApiV5ModelsStatisticsItemDetail

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsItemDetail from a JSON string
hello_asso_api_v5_models_statistics_item_detail_instance = HelloAssoApiV5ModelsStatisticsItemDetail.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsItemDetail.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_item_detail_dict = hello_asso_api_v5_models_statistics_item_detail_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsItemDetail from a dict
hello_asso_api_v5_models_statistics_item_detail_from_dict = HelloAssoApiV5ModelsStatisticsItemDetail.from_dict(hello_asso_api_v5_models_statistics_item_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


