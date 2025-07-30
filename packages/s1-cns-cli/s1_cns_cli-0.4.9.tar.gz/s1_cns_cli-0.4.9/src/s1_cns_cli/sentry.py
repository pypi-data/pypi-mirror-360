import os, logging
import sentry_sdk as sentry
from s1_cns_cli.cli.utils import read_json_file
from s1_cns_cli.cli.registry import CONFIG_FILE_NAME


def remove_keys(event, hint):
    if "logger" in event:
        return None
    if "extra" in event and "sys.argv" in event["extra"]:
        system_args = event["extra"]["sys.argv"]
        keys_to_exclude_from_args = ["--api-token"]
        for key in keys_to_exclude_from_args:
            try:
                index = system_args.index(key)
                del system_args[index:index+2]
            except ValueError:
                pass
    return event


def init_sentry(cache_directory):
    # disable sentry logging
    logger = logging.getLogger("sentry_sdk.errors")
    connection_pool_logger = logging.getLogger("urllib3.connectionpool")

    logger.addFilter(lambda record: False)
    connection_pool_logger.setLevel(logging.ERROR)

    global_config_data = read_json_file(os.path.join(cache_directory, CONFIG_FILE_NAME))
    if "sentry_dsn" in global_config_data:
        sentry.init(dsn=global_config_data["sentry_dsn"], before_send=remove_keys, before_send_transaction=remove_keys,
                    traces_sample_rate=1.0)


def drain_sentry():
    client = sentry.Hub.current.client
    if client is not None:
        client.close(timeout=2.0, callback=lambda x, y: None)
