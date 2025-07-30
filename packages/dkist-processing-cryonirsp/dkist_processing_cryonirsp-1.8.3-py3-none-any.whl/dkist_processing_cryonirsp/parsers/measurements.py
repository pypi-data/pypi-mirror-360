"""Copies of UniqueBud and SingleValueSingleKeyFlower from common that only activate if the frames are "observe" task."""
from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import UniqueBud

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.tags import CryonirspStemName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess


class NumberOfMeasurementsBud(UniqueBud):
    """Bud for finding the total number of measurements per scan step."""

    def __init__(self):
        self.metadata_key = "num_meas"
        super().__init__(
            constant_name=CryonirspBudName.num_meas.value, metadata_key=self.metadata_key
        )

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> Type[SpilledDirt] | int:
        """
        Setter for the bud.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return getattr(fits_obj, self.metadata_key)


class MeasurementNumberFlower(SingleValueSingleKeyFlower):
    """Flower for a measurement number."""

    def __init__(self):
        super().__init__(tag_stem_name=CryonirspStemName.meas_num.value, metadata_key="meas_num")

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> Type[SpilledDirt] | int:
        """
        Setter for a flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return super().setter(fits_obj)
