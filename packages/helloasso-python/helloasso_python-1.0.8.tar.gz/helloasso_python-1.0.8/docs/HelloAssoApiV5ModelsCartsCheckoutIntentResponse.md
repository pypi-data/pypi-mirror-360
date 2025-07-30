# HelloAssoApiV5ModelsCartsCheckoutIntentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | **object** | Metadata (Json object)  Only if metadata were sent on the checkout form initialization | [optional] 
**order** | [**HelloAssoApiV5ModelsStatisticsOrderDetail**](HelloAssoApiV5ModelsStatisticsOrderDetail.md) |  | [optional] 
**id** | **int** | Id of the checkout intent | [optional] 
**redirect_url** | **str** | Url where the contributor must be redirected to | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_carts_checkout_intent_response import HelloAssoApiV5ModelsCartsCheckoutIntentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsCartsCheckoutIntentResponse from a JSON string
hello_asso_api_v5_models_carts_checkout_intent_response_instance = HelloAssoApiV5ModelsCartsCheckoutIntentResponse.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsCartsCheckoutIntentResponse.to_json())

# convert the object into a dict
hello_asso_api_v5_models_carts_checkout_intent_response_dict = hello_asso_api_v5_models_carts_checkout_intent_response_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsCartsCheckoutIntentResponse from a dict
hello_asso_api_v5_models_carts_checkout_intent_response_from_dict = HelloAssoApiV5ModelsCartsCheckoutIntentResponse.from_dict(hello_asso_api_v5_models_carts_checkout_intent_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


