# ResultsWithPaginationModelOrder

ResultsWithPaginationModel class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[HelloAssoApiV5ModelsStatisticsOrder]**](HelloAssoApiV5ModelsStatisticsOrder.md) | Data property | [optional] 
**pagination** | [**HelloAssoApiV5ModelsCommonPaginationModel**](HelloAssoApiV5ModelsCommonPaginationModel.md) |  | [optional] 

## Example

```python
from helloasso_python.models.results_with_pagination_model_order import ResultsWithPaginationModelOrder

# TODO update the JSON string below
json = "{}"
# create an instance of ResultsWithPaginationModelOrder from a JSON string
results_with_pagination_model_order_instance = ResultsWithPaginationModelOrder.from_json(json)
# print the JSON string representation of the object
print(ResultsWithPaginationModelOrder.to_json())

# convert the object into a dict
results_with_pagination_model_order_dict = results_with_pagination_model_order_instance.to_dict()
# create an instance of ResultsWithPaginationModelOrder from a dict
results_with_pagination_model_order_from_dict = ResultsWithPaginationModelOrder.from_dict(results_with_pagination_model_order_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


