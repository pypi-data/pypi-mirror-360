"""Configuration for the dkist-processing-cryonirsp package and the logging thereof."""
from dkist_processing_common.config import DKISTProcessingCommonConfiguration


class DKISTProcessingCryoNIRSPConfigurations(DKISTProcessingCommonConfiguration):
    """Configurations custom to the dkist-processing-cryonirsp package."""

    pass  # nothing custom yet


dkist_processing_cryonirsp_configurations = DKISTProcessingCryoNIRSPConfigurations()
dkist_processing_cryonirsp_configurations.log_configurations()
