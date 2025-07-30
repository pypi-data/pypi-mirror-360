# ResultsWithPaginationModelItem

ResultsWithPaginationModel class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[HelloAssoApiV5ModelsStatisticsItem]**](HelloAssoApiV5ModelsStatisticsItem.md) | Data property | [optional] 
**pagination** | [**HelloAssoApiV5ModelsCommonPaginationModel**](HelloAssoApiV5ModelsCommonPaginationModel.md) |  | [optional] 

## Example

```python
from helloasso_python.models.results_with_pagination_model_item import ResultsWithPaginationModelItem

# TODO update the JSON string below
json = "{}"
# create an instance of ResultsWithPaginationModelItem from a JSON string
results_with_pagination_model_item_instance = ResultsWithPaginationModelItem.from_json(json)
# print the JSON string representation of the object
print(ResultsWithPaginationModelItem.to_json())

# convert the object into a dict
results_with_pagination_model_item_dict = results_with_pagination_model_item_instance.to_dict()
# create an instance of ResultsWithPaginationModelItem from a dict
results_with_pagination_model_item_from_dict = ResultsWithPaginationModelItem.from_dict(results_with_pagination_model_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


