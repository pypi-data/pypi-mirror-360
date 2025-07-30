# HelloAssoApiV5ModelsCartsCheckoutTerm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **int** | Term amount, all taxes included, in cents | 
**var_date** | **datetime** | Term date | 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_carts_checkout_term import HelloAssoApiV5ModelsCartsCheckoutTerm

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsCartsCheckoutTerm from a JSON string
hello_asso_api_v5_models_carts_checkout_term_instance = HelloAssoApiV5ModelsCartsCheckoutTerm.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsCartsCheckoutTerm.to_json())

# convert the object into a dict
hello_asso_api_v5_models_carts_checkout_term_dict = hello_asso_api_v5_models_carts_checkout_term_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsCartsCheckoutTerm from a dict
hello_asso_api_v5_models_carts_checkout_term_from_dict = HelloAssoApiV5ModelsCartsCheckoutTerm.from_dict(hello_asso_api_v5_models_carts_checkout_term_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


