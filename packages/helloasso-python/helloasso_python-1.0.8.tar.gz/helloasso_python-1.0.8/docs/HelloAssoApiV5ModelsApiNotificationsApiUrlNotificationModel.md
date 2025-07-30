# HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel

Organization notification URL Model class

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** | The notification Url | [optional] 
**api_notification_type** | [**HelloAssoApiV5ModelsApiNotificationsApiNotificationType**](HelloAssoApiV5ModelsApiNotificationsApiNotificationType.md) |  | [optional] 
**signature_key** | **str** | Signature Key : allows you to verify the authenticity of notifications | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_api_v5_models_api_notifications_api_url_notification_model import HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel from a JSON string
hello_asso_api_v5_models_api_notifications_api_url_notification_model_instance = HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel.from_json(json)
# print the JSON string representation of the object
print(HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel.to_json())

# convert the object into a dict
hello_asso_api_v5_models_api_notifications_api_url_notification_model_dict = hello_asso_api_v5_models_api_notifications_api_url_notification_model_instance.to_dict()
# create an instance of HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel from a dict
hello_asso_api_v5_models_api_notifications_api_url_notification_model_from_dict = HelloAssoApiV5ModelsApiNotificationsApiUrlNotificationModel.from_dict(hello_asso_api_v5_models_api_notifications_api_url_notification_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


