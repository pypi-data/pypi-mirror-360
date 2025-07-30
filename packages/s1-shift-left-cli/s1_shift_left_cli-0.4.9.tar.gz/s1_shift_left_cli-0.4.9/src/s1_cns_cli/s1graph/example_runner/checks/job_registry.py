#
# No change required normally except to possibly switch it to json
# eg. from s1_cns_cli.s1graph.json_doc.base_registry import Registry
#
from s1_cns_cli.s1graph.common.s1cns.check_type import CheckType
from s1_cns_cli.s1graph.yaml_doc.base_registry import Registry

registry = Registry(CheckType.YAML)
