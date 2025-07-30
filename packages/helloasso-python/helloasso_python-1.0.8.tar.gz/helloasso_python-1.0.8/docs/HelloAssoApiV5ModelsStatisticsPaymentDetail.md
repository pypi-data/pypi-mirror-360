# HelloAssoApiV5ModelsStatisticsPaymentDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order** | [**HelloAssoApiV5ModelsStatisticsOrderLight**](HelloAssoApiV5ModelsStatisticsOrderLight.md) |  | [optional] 
**payer** | [**HelloAssoApiV5ModelsStatisticsPayer**](HelloAssoApiV5ModelsStatisticsPayer.md) |  | [optional] 
**items** | [**List[HelloAssoApiV5ModelsStatisticsPaymentItem]**](HelloAssoApiV5ModelsStatisticsPaymentItem.md) | Items linked to this payment | [optional] 
**cash_out_date** | **datetime** | The date of the cash out | [optional] 
**cash_out_state** | [**HelloAssoApiV5ModelsEnumsPaymentCashOutState**](HelloAssoApiV5ModelsEnumsPaymentCashOutState.md) |  | [optional] 
**payment_receipt_url** | **str** | The Payment Receipt Url | [optional] 
**fiscal_receipt_url** | **str** | The Fiscal Receipt Url | [optional] 
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
from helloasso_python.models.hello_asso_api_v5_models_statistics_payment_detail import HelloAssoApiV5ModelsStatisticsPaymentDetail

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsPaymentDetail from a JSON string
hello_asso_api_v5_models_statistics_payment_detail_instance = HelloAssoApiV5ModelsStatisticsPaymentDetail.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsPaymentDetail.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_payment_detail_dict = hello_asso_api_v5_models_statistics_payment_detail_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsPaymentDetail from a dict
hello_asso_api_v5_models_statistics_payment_detail_from_dict = HelloAssoApiV5ModelsStatisticsPaymentDetail.from_dict(hello_asso_api_v5_models_statistics_payment_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


