# HelloAssoApiV5ModelsPaymentPublicPaymentModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The payment id | [optional] 
**organization_id** | **int** | The Organization id, which the payment was made to | [optional] 
**form_id** | **int** | The form id where the payment was made. Used with FormType | [optional] 
**form_type** | [**HelloAssoApiV5ModelsEnumsFormType**](HelloAssoApiV5ModelsEnumsFormType.md) |  | [optional] 
**amount** | **int** | Amount | [optional] 
**means_payment** | [**HelloAssoApiV5ModelsEnumsPaymentMeans**](HelloAssoApiV5ModelsEnumsPaymentMeans.md) |  | [optional] 
**cash_out_state** | [**HelloAssoApiV5ModelsEnumsPaymentCashOutState**](HelloAssoApiV5ModelsEnumsPaymentCashOutState.md) |  | [optional] 
**var_date** | **datetime** | The payment Date. | [optional] 
**authorization_date** | **datetime** | If the payment is authorized, this is the date of authorization | [optional] 
**order_date** | **datetime** | Date at which the Order was placed.  Important for monthly payments or scheduled payments. | [optional] 
**order_id** | **int** | The id of the order | [optional] 
**fiscal_receipt_generated** | **bool** | Whether a Fiscal receipt document has been generated for this payment or not. | [optional] 
**payer_first_name** | **str** | The inputted payer first name, might differs from User firstname, from linked user Id | [optional] 
**payer_last_name** | **str** | The inputted payer last name,  might differs from User lastname, from linked user Id | [optional] 
**status** | [**HelloAssoApiV5ModelsEnumsPaymentState**](HelloAssoApiV5ModelsEnumsPaymentState.md) |  | [optional] 
**user_id** | **int** | The user id who initiated the payment | [optional] 
**user_first_name** | **str** | The name of the user who initiated the payment. May differ from PayerFirstName | [optional] 
**user_last_name** | **str** | The name of the user who initiated the payment. May differ from PayerLastName | [optional] 
**user_email** | **str** | The email of the user account who initiated the payment. | [optional] 
**provider_title** | **str** | name of the provider | [optional] 
**installment_number** | **int** | Indicates the payment number (useful in the case of an order comprising payments with installments)  Starting with 1. | [optional] 
**meta** | [**HelloAssoApiV5ModelsCommonMetaModel**](HelloAssoApiV5ModelsCommonMetaModel.md) |  | [optional] 
**refund_operations** | [**List[HelloAssoApiV5ModelsStatisticsRefundOperationLightModel]**](HelloAssoApiV5ModelsStatisticsRefundOperationLightModel.md) | The refund operations for the specific payment. | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_payment_public_payment_model import HelloAssoApiV5ModelsPaymentPublicPaymentModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsPaymentPublicPaymentModel from a JSON string
hello_asso_api_v5_models_payment_public_payment_model_instance = HelloAssoApiV5ModelsPaymentPublicPaymentModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsPaymentPublicPaymentModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_payment_public_payment_model_dict = hello_asso_api_v5_models_payment_public_payment_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsPaymentPublicPaymentModel from a dict
hello_asso_api_v5_models_payment_public_payment_model_from_dict = HelloAssoApiV5ModelsPaymentPublicPaymentModel.from_dict(hello_asso_api_v5_models_payment_public_payment_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


