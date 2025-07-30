from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class S3BlockPublicPolicy(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure S3 bucket has block public policy enabled"
        id = "CKV_AWS_54"
        supported_resources = ['aws_s3_bucket_public_access_block']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "block_public_policy"


scanner = S3BlockPublicPolicy()
