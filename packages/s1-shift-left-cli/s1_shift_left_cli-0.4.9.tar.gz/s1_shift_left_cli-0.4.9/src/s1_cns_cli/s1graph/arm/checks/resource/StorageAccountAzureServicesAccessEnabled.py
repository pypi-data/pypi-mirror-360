from s1_cns_cli.s1graph.arm.base_resource_check import BaseResourceCheck
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
# https://docs.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts
from s1_cns_cli.s1graph.common.util.type_forcers import force_int


class StorageAccountAzureServicesAccessEnabled(BaseResourceCheck):
    def __init__(self):
        # properties.networkAcls.bypass == "AzureServices"
        # Fail if apiVersion less than 2017 as this setting wasn't available
        name = "Ensure 'Trusted Microsoft Services' is enabled for Storage Account access"
        id = "CKV_AZURE_36"
        supported_resources = ['Microsoft.Storage/storageAccounts']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "apiVersion" in conf:
            # Fail if apiVersion < 2017 as you could not set networkAcls
            year = force_int(conf["apiVersion"][0:4])

            if year is None:
                return CheckResult.UNKNOWN  # Should be handled by variable rendering
            if year < 2017:
                return CheckResult.FAILED

        if "properties" in conf:
            if "networkAcls" in conf["properties"]:
                if "defaultAction" in conf["properties"]["networkAcls"]:
                    if not isinstance(conf["properties"]["networkAcls"], dict):
                        return CheckResult.UNKNOWN
                    if conf["properties"]["networkAcls"]["defaultAction"] == "Allow":
                        return CheckResult.PASSED
                    elif "bypass" in conf["properties"]["networkAcls"] and \
                            conf["properties"]["networkAcls"]["bypass"] == "AzureServices":
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = StorageAccountAzureServicesAccessEnabled()
