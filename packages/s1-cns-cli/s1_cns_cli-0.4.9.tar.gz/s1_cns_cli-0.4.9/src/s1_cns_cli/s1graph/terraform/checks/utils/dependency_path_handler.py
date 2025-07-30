import os
from typing import List
from s1_cns_cli.s1graph.common.runners.base_runner import strtobool

PATH_SEPARATOR = "->"


def unify_dependency_path(dependency_path: List[str]) -> str:
    if not dependency_path:
        return ''
    if strtobool(os.getenv('SENTINELONE_CNS_ENABLE_NESTED_MODULES', 'True')):
        return dependency_path[-1]
    return PATH_SEPARATOR.join(dependency_path)
