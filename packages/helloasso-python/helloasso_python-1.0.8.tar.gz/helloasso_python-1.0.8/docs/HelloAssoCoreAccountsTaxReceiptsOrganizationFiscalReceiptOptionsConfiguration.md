# HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**purpose** | **str** |  | [optional] 
**cerfa_type_id** | **int** |  | [optional] 
**jo_category_id** | **int** |  | [optional] 
**format_option_model** | [**HelloAssoModelsPaymentsCashInFiscalReceiptFiscalReceiptFormatOption**](HelloAssoModelsPaymentsCashInFiscalReceiptFiscalReceiptFormatOption.md) |  | [optional] 
**signatory_model** | [**HelloAssoModelsAccountsOrganizationLegalInformationsFiscalReceiptSignatoryModel**](HelloAssoModelsAccountsOrganizationLegalInformationsFiscalReceiptSignatoryModel.md) |  | [optional] 
**address_model** | [**HaTrustContractLegalInformationAddressAddressDto**](HaTrustContractLegalInformationAddressAddressDto.md) |  | [optional] 

## Example

```python
from helloasso_python.models.hello_asso_core_accounts_tax_receipts_organization_fiscal_receipt_options_configuration import HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration from a JSON string
hello_asso_core_accounts_tax_receipts_organization_fiscal_receipt_options_configuration_instance = HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration.from_json(json)
# print the JSON string representation of the object
print(HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration.to_json())

# convert the object into a dict
hello_asso_core_accounts_tax_receipts_organization_fiscal_receipt_options_configuration_dict = hello_asso_core_accounts_tax_receipts_organization_fiscal_receipt_options_configuration_instance.to_dict()
# create an instance of HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration from a dict
hello_asso_core_accounts_tax_receipts_organization_fiscal_receipt_options_configuration_from_dict = HelloAssoCoreAccountsTaxReceiptsOrganizationFiscalReceiptOptionsConfiguration.from_dict(hello_asso_core_accounts_tax_receipts_organization_fiscal_receipt_options_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


