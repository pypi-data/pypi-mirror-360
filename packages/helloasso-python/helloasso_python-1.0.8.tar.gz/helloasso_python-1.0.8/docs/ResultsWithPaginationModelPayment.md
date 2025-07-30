# ResultsWithPaginationModelPayment

ResultsWithPaginationModel class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[HelloAssoApiV5ModelsStatisticsPayment]**](HelloAssoApiV5ModelsStatisticsPayment.md) | Data property | [optional] 
**pagination** | [**HelloAssoApiV5ModelsCommonPaginationModel**](HelloAssoApiV5ModelsCommonPaginationModel.md) |  | [optional] 

## Example

```python
from helloasso_python.models.results_with_pagination_model_payment import ResultsWithPaginationModelPayment

# TODO update the JSON string below
json = "{}"
# create an instance of ResultsWithPaginationModelPayment from a JSON string
results_with_pagination_model_payment_instance = ResultsWithPaginationModelPayment.from_json(json)
# print the JSON string representation of the object
print(ResultsWithPaginationModelPayment.to_json())

# convert the object into a dict
results_with_pagination_model_payment_dict = results_with_pagination_model_payment_instance.to_dict()
# create an instance of ResultsWithPaginationModelPayment from a dict
results_with_pagination_model_payment_from_dict = ResultsWithPaginationModelPayment.from_dict(results_with_pagination_model_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


