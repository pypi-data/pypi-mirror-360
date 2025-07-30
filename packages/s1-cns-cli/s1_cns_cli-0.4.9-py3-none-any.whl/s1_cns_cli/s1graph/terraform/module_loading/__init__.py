# the order is important, because it reflects the order, which will be used to download the module
from s1_cns_cli.s1graph.terraform.module_loading.loaders.registry_loader import RegistryLoader  # noqa
from s1_cns_cli.s1graph.terraform.module_loading.loaders.git_loader import GenericGitLoader  # noqa
from s1_cns_cli.s1graph.terraform.module_loading.loaders.github_loader import GithubLoader  # noqa
from s1_cns_cli.s1graph.terraform.module_loading.loaders.bitbucket_loader import BitbucketLoader  # noqa
from s1_cns_cli.s1graph.terraform.module_loading.loaders.github_access_token_loader import GithubAccessTokenLoader  # noqa
from s1_cns_cli.s1graph.terraform.module_loading.loaders.bitbucket_access_token_loader import BitbucketAccessTokenLoader  # noqa
from s1_cns_cli.s1graph.terraform.module_loading.loaders.local_path_loader import LocalPathLoader  # noqa
