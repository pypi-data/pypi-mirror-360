# HaTrustContractLegalInformationAddressAddressDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**line** | **str** |  | [optional] 
**city** | **str** |  | [optional] 
**zip_code** | **str** |  | [optional] 
**country** | **int** |  | [optional] 
**country_name** | **str** |  | [optional] 
**country_alpha3** | **str** |  | [optional] 

## Example

```python
from helloasso_python.models.ha_trust_contract_legal_information_address_address_dto import HaTrustContractLegalInformationAddressAddressDto

# TODO update the JSON string below
json = "{}"
# create an instance of HaTrustContractLegalInformationAddressAddressDto from a JSON string
ha_trust_contract_legal_information_address_address_dto_instance = HaTrustContractLegalInformationAddressAddressDto.from_json(json)
# print the JSON string representation of the object
print(HaTrustContractLegalInformationAddressAddressDto.to_json())

# convert the object into a dict
ha_trust_contract_legal_information_address_address_dto_dict = ha_trust_contract_legal_information_address_address_dto_instance.to_dict()
# create an instance of HaTrustContractLegalInformationAddressAddressDto from a dict
ha_trust_contract_legal_information_address_address_dto_from_dict = HaTrustContractLegalInformationAddressAddressDto.from_dict(ha_trust_contract_legal_information_address_address_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


