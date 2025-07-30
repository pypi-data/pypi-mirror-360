# HelloAssoApiV5ModelsStatisticsSharePayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Id of the payment | [optional] 
**share_amount** | **int** | Amount of the item payed on this payment term (in cents) | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_share_payment import HelloAssoApiV5ModelsStatisticsSharePayment

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsSharePayment from a JSON string
hello_asso_api_v5_models_statistics_share_payment_instance = HelloAssoApiV5ModelsStatisticsSharePayment.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsSharePayment.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_share_payment_dict = hello_asso_api_v5_models_statistics_share_payment_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsSharePayment from a dict
hello_asso_api_v5_models_statistics_share_payment_from_dict = HelloAssoApiV5ModelsStatisticsSharePayment.from_dict(hello_asso_api_v5_models_statistics_share_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


