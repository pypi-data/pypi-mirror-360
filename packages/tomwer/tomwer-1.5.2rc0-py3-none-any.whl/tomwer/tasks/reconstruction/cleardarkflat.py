"""
Contains task to clear reduced dark and flat frames
"""

from __future__ import annotations

from tomoscan.scanbase import TomoScanBase as TomoscanScanBase

from processview.core.manager import DatasetState, ProcessManager
from processview.core.superviseprocess import SuperviseProcess

from tomwer.tasks.task import Task
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.utils.scanutils import data_identifier_to_scan
from tomwer.core.reconstruction.darkflat import params as dkrf_reconsparams
from tomwer.utils import docstring


class ClearReducedDarkAndFlat(
    Task,
    SuperviseProcess,
    input_names=("data",),
    output_names=("data",),
):
    """
    Task to clear reduced darks and flats. Both on disk and on the object cache.
    th goal of this task is to make sure the scan is cleared of any reduced frames to reprocess it later.
    """

    def run(self):
        scan = self.inputs.data
        if not isinstance(scan, TomoscanScanBase):
            raise TypeError(
                f"scan should be an instance of {TomoscanScanBase}. Got {type(scan)}"
            )
        scan.set_reduced_flats(None)
        scan.reduced_flats_infos = None
        scan.set_reduced_darks(None)
        scan.reduced_darks_infos = None

        self.outputs.data = scan
