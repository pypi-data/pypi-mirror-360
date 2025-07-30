# HelloAssoApiV5ModelsStatisticsShareItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Id of the order item | [optional] 
**share_amount** | **int** | Amount of the payment assigned to the item and its options (in cents) | [optional] 
**share_item_amount** | **int** | Amount of the item payed on this payment term (in cents) | [optional] 
**share_options_amount** | **int** | Amount of all extra options linked to this item and payed on this payment (in cents) | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_share_item import HelloAssoApiV5ModelsStatisticsShareItem

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsShareItem from a JSON string
hello_asso_api_v5_models_statistics_share_item_instance = HelloAssoApiV5ModelsStatisticsShareItem.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsShareItem.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_share_item_dict = hello_asso_api_v5_models_statistics_share_item_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsShareItem from a dict
hello_asso_api_v5_models_statistics_share_item_from_dict = HelloAssoApiV5ModelsStatisticsShareItem.from_dict(hello_asso_api_v5_models_statistics_share_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


