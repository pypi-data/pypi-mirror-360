# ResultsWithPaginationModelFormLightModel

ResultsWithPaginationModel class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[HelloAssoApiV5ModelsFormsFormLightModel]**](HelloAssoApiV5ModelsFormsFormLightModel.md) | Data property | [optional] 
**pagination** | [**HelloAssoApiV5ModelsCommonPaginationModel**](HelloAssoApiV5ModelsCommonPaginationModel.md) |  | [optional] 

## Example

```python
from helloasso_python.models.results_with_pagination_model_form_light_model import ResultsWithPaginationModelFormLightModel

# TODO update the JSON string below
json = "{}"
# create an instance of ResultsWithPaginationModelFormLightModel from a JSON string
results_with_pagination_model_form_light_model_instance = ResultsWithPaginationModelFormLightModel.from_json(json)
# print the JSON string representation of the object
print(ResultsWithPaginationModelFormLightModel.to_json())

# convert the object into a dict
results_with_pagination_model_form_light_model_dict = results_with_pagination_model_form_light_model_instance.to_dict()
# create an instance of ResultsWithPaginationModelFormLightModel from a dict
results_with_pagination_model_form_light_model_from_dict = ResultsWithPaginationModelFormLightModel.from_dict(results_with_pagination_model_form_light_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


