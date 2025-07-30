from typing import Dict, List, Any, Optional

from s1_cns_cli.s1graph.common.util.type_forcers import force_dict


def get_resource_tags(entity_config: Dict[str, List[Any]]) -> Optional[Dict[str, Any]]:
    return force_dict(entity_config.get("labels"))
