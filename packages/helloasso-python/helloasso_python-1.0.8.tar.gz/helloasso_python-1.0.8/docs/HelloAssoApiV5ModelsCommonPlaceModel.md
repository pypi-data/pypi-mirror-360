# HelloAssoApiV5ModelsCommonPlaceModel

PlaceModel class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address** | **str** | Address | [optional] 
**name** | **str** | Name of the place | [optional] 
**city** | **str** | City | [optional] 
**zip_code** | **str** | ZipCode | [optional] 
**country** | **str** | 3 letter country code | [optional] 
**geo_location** | [**HelloAssoModelsSharedGeoLocation**](HelloAssoModelsSharedGeoLocation.md) |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_common_place_model import HelloAssoApiV5ModelsCommonPlaceModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsCommonPlaceModel from a JSON string
hello_asso_api_v5_models_common_place_model_instance = HelloAssoApiV5ModelsCommonPlaceModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsCommonPlaceModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_common_place_model_dict = hello_asso_api_v5_models_common_place_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsCommonPlaceModel from a dict
hello_asso_api_v5_models_common_place_model_from_dict = HelloAssoApiV5ModelsCommonPlaceModel.from_dict(hello_asso_api_v5_models_common_place_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


