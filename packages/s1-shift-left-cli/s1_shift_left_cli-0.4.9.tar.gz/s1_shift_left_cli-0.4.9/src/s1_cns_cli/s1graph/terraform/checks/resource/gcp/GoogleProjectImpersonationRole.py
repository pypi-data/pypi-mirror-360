from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.gcp.AbsGoogleImpersonationRoles import AbsGoogleImpersonationRoles


class GoogleProjectImpersonationRoles(AbsGoogleImpersonationRoles):
    def __init__(self) -> None:
        name = "Ensure roles do not impersonate or manage Service Accounts used at project level"
        id = "CKV_GCP_49"
        supported_resources = ('google_project_iam_member', 'google_project_iam_binding')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleProjectImpersonationRoles()
