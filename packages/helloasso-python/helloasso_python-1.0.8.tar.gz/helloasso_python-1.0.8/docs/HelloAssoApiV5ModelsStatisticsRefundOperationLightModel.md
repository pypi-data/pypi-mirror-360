# HelloAssoApiV5ModelsStatisticsRefundOperationLightModel

The refund operation with the Id, amount, amount tip and the status.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The refund operation identifier. | [optional] 
**amount** | **int** | The amount for this refund. | [optional] 
**amount_tip** | **int** | The amount tip for this refund. | [optional] 
**status** | [**HelloAssoApiV5ModelsEnumsOperationState**](HelloAssoApiV5ModelsEnumsOperationState.md) |  | [optional] 
**meta** | [**HelloAssoApiV5ModelsCommonMetaModel**](HelloAssoApiV5ModelsCommonMetaModel.md) |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_refund_operation_light_model import HelloAssoApiV5ModelsStatisticsRefundOperationLightModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsRefundOperationLightModel from a JSON string
hello_asso_api_v5_models_statistics_refund_operation_light_model_instance = HelloAssoApiV5ModelsStatisticsRefundOperationLightModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsRefundOperationLightModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_refund_operation_light_model_dict = hello_asso_api_v5_models_statistics_refund_operation_light_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsRefundOperationLightModel from a dict
hello_asso_api_v5_models_statistics_refund_operation_light_model_from_dict = HelloAssoApiV5ModelsStatisticsRefundOperationLightModel.from_dict(hello_asso_api_v5_models_statistics_refund_operation_light_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


