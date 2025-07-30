# HelloAssoApiV5ModelsCommonPaginationModel

Pagination model class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page_size** | **int** | Page size | [optional] 
**total_count** | **int** | Total number of results available | [optional] 
**page_index** | **int** | Current page index | [optional] 
**total_pages** | **int** | Total number of pages of results with current page size | [optional] 
**continuation_token** | **str** | Continuation Token to get next results | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_common_pagination_model import HelloAssoApiV5ModelsCommonPaginationModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsCommonPaginationModel from a JSON string
hello_asso_api_v5_models_common_pagination_model_instance = HelloAssoApiV5ModelsCommonPaginationModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsCommonPaginationModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_common_pagination_model_dict = hello_asso_api_v5_models_common_pagination_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsCommonPaginationModel from a dict
hello_asso_api_v5_models_common_pagination_model_from_dict = HelloAssoApiV5ModelsCommonPaginationModel.from_dict(hello_asso_api_v5_models_common_pagination_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


