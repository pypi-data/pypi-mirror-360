# HelloAssoApiV5ModelsStatisticsOrderLight


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The ID of the Order | [optional] 
**var_date** | **datetime** | Order creation date | [optional] 
**form_slug** | **str** | FormSlug (lowercase name of the form without special characters) | [optional] 
**form_type** | [**HelloAssoApiV5ModelsEnumsFormType**](HelloAssoApiV5ModelsEnumsFormType.md) |  | [optional] 
**organization_name** | **str** | The organization name. | [optional] 
**organization_slug** | **str** | OrganizationSlug (lowercase name of the organization without special characters) | [optional] 
**organization_type** | [**HelloAssoApiV5ModelsEnumsOrganizationType**](HelloAssoApiV5ModelsEnumsOrganizationType.md) |  | [optional] 
**organization_is_under_coluche_law** | **bool** | Whether or not the organization is subject to the coluche law | [optional] 
**checkout_intent_id** | **int** | Checkout intent Id if available | [optional] 
**meta** | [**HelloAssoApiV5ModelsCommonMetaModel**](HelloAssoApiV5ModelsCommonMetaModel.md) |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_statistics_order_light import HelloAssoApiV5ModelsStatisticsOrderLight

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsStatisticsOrderLight from a JSON string
hello_asso_api_v5_models_statistics_order_light_instance = HelloAssoApiV5ModelsStatisticsOrderLight.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsStatisticsOrderLight.to_json())

# convert the object into a dict
hello_asso_api_v5_models_statistics_order_light_dict = hello_asso_api_v5_models_statistics_order_light_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsStatisticsOrderLight from a dict
hello_asso_api_v5_models_statistics_order_light_from_dict = HelloAssoApiV5ModelsStatisticsOrderLight.from_dict(hello_asso_api_v5_models_statistics_order_light_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


