""" Initialize most extensions used throughout application
"""
import logging

logger = logging.getLogger(__name__)

try:
    # Client packages *should* provide a `pypeline.yaml` file. This
    # loads the configuration file with the provided name of the client
    # package (e.g. pypeline_demo)
    from pypeline.pypeline_yaml import load_client_config_and_version

    pypeline_config, pypeline_client_version = load_client_config_and_version()
except Exception as e:
    pypeline_config = None
    pypeline_client_version = None
    logger.warning("Unable to load client Pypeline config ... {}".format(e))
