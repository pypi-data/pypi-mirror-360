# HelloAssoApiV5ModelsStatisticsItemPayment

Payment linked to the item

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cash_out_state** | [**HelloAssoApiV5ModelsEnumsPaymentCashOutState**](HelloAssoApiV5ModelsEnumsPaymentCashOutState.md) |  | [optional] 
**share_amount** | **int** | Amount of the item and extra options payed on this payment term (in cents) | [optional] 
**id** | **int** | The ID of the payment | [optional] 
**amount** | **int** | Total Amount of the payment (in cents) | [optional] 
**amount_tip** | **int** | Tip Amount of the payment (in cents) | [optional] 
**var_date** | **datetime** | Date of the payment | [optional] 
**payment_means** | [**HelloAssoApiV5ModelsEnumsPaymentMeans**](HelloAssoApiV5ModelsEnumsPaymentMeans.md) |  | [optional] 
**installment_number** | **int** | Indicates the payment number (useful in the case of an order comprising payments with installments) | [optional] 
**state** | [**HelloAssoApiV5ModelsEnumsPaymentState**](HelloAssoApiV5ModelsEnumsPaymentState.md) |  | [optional] 
**type** | [**HelloAssoApiV5ModelsEnumsPaymentType**](HelloAssoApiV5ModelsEnumsPaymentType.md) |  | [optional] 
**meta** | [**HelloAssoApiV5ModelsCommonMetaModel**](HelloAssoApiV5ModelsCommonMetaModel.md) |  | [optional] 
**payment_off_line_mean** | [**HelloAssoApiV5ModelsEnumsPaymentMeans**](HelloAssoApiV5ModelsEnumsPaymentMeans.md) |  | [optional] 
**refund_operations** | [**List[HelloAssoApiV5ModelsStatisticsRefundOperationLightModel]**](HelloAssoApiV5ModelsStatisticsRefundOperationLightModel.md) | The refund operations information for the specific payment. | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_item_payment import HelloAssoApiV5ModelsStatisticsItemPayment

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsItemPayment from a JSON string
hello_asso_api_v5_models_statistics_item_payment_instance = HelloAssoApiV5ModelsStatisticsItemPayment.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsItemPayment.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_item_payment_dict = hello_asso_api_v5_models_statistics_item_payment_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsItemPayment from a dict
hello_asso_api_v5_models_statistics_item_payment_from_dict = HelloAssoApiV5ModelsStatisticsItemPayment.from_dict(hello_asso_api_v5_models_statistics_item_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


