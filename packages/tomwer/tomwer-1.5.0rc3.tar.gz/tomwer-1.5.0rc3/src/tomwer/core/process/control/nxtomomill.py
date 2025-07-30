# coding: utf-8

from __future__ import annotations


import logging
import os
import pathlib

from tomoscan.series import Series

from nxtomomill import converter as nxtomomill_converter
from nxtomomill.io.config import TomoEDFConfig as EDFConfig
from nxtomomill.io.config import TomoHDF5Config as HDF5Config
from nxtomomill.converter.hdf5.utils import (
    get_default_output_file,
)

from tomwer.io.utils.raw_and_processed_data import to_raw_data_path
from tomwer.core.process.output import ProcessDataOutputDirMode
from tomwer.core.process.task import TaskWithProgress
from tomwer.core.scan.nxtomoscan import NXtomoScan
from tomwer.core.utils.scanutils import format_output_location

_logger = logging.getLogger(__name__)


class H5ToNxProcess(
    TaskWithProgress,
    input_names=("h5_to_nx_configuration",),
    optional_input_names=(
        "progress",
        "bliss_scan",
        "serialize_output_data",
    ),
    output_names=("data", "series"),
):
    """
    Task to convert from a bliss dataset to a nexus compliant dataset
    """

    @staticmethod
    def deduce_output_file_path(master_file_name, scan, entry, outputdir):
        master_file_name = os.path.abspath(master_file_name)
        # step 1: get output dir
        try:
            outputdir = ProcessDataOutputDirMode.from_value(outputdir)
        except ValueError:
            # case path provided directly
            output_folder = format_output_location(outputdir, scan=scan)
        else:
            if outputdir is ProcessDataOutputDirMode.OTHER:
                raise ValueError(
                    f"When output dir mode is {ProcessDataOutputDirMode.OTHER} we expect to received the output dir directly"
                )
            if outputdir is ProcessDataOutputDirMode.PROCESSED_DATA_FOLDER:
                path = pathlib.Path(
                    get_default_output_file(input_file=master_file_name)
                )
                output_folder = str(path.parent)
            elif outputdir is ProcessDataOutputDirMode.IN_SCAN_FOLDER:
                output_folder = os.path.dirname(master_file_name)
            else:
                raise RuntimeError(f"output dir {outputdir} not handled")

        file_name = os.path.basename(master_file_name)
        if "." in file_name:
            file_name = "".join(file_name.split(".")[:-1])

        entry_for_file_name = entry.lstrip("/")
        entry_for_file_name = entry_for_file_name.replace("/", "_")
        entry_for_file_name = entry_for_file_name.replace(".", "_")
        entry_for_file_name = entry_for_file_name.replace(":", "_")
        output_file_name = "_".join(
            (os.path.splitext(file_name)[0], entry_for_file_name + ".nx")
        )
        return os.path.join(output_folder, output_file_name)

    def run(self):
        config = self.inputs.h5_to_nx_configuration
        if isinstance(config, dict):
            config = HDF5Config.from_dict(config)
        elif not isinstance(config, HDF5Config):
            raise TypeError(
                "h5_to_nx_configuration should be a dict or an instance of {HDF5Config}"
            )
        config.bam_single_file = True
        config.no_master_file = True
        try:
            convs = nxtomomill_converter.from_h5_to_nx(
                configuration=config, progress=self.progress
            )
        except Exception as e:
            _logger.error(e)
            return

        if len(convs) == 0:
            return

        series = []
        for conv in convs:
            conv_file, conv_entry = conv
            scan_converted = NXtomoScan(scan=conv_file, entry=conv_entry)
            _logger.processSucceed(
                f"{config.input_file} {config.entries} has been translated to {scan_converted}"
            )
            if self.get_input_value("serialize_output_data", True):
                data = scan_converted.to_dict()
            else:
                data = scan_converted
            series.append(data)
        self.outputs.series = Series(
            name=f"series created from {config.input_file}", iterable=series
        )
        self.outputs.data = series[-1] if len(series) > 0 else None


class EDFToNxProcess(
    TaskWithProgress,
    input_names=("edf_to_nx_configuration",),
    optional_input_names=(
        "progress",
        "edf_scan",
        "serialize_output_data",
    ),
    output_names=("data",),
):
    """
    Task calling edf2nx in order to insure conversion from .edf to .nx (create one NXtomo to be used elsewhere)
    """

    def run(self):
        config = self.inputs.edf_to_nx_configuration
        if isinstance(config, dict):
            config = EDFConfig.from_dict(config)
        elif not isinstance(config, EDFConfig):
            raise TypeError(
                "edf_to_nx_configuration should be a dict or an instance of {TomoEDFConfig}"
            )
        os.makedirs(os.path.dirname(config.output_file), exist_ok=True)
        file_path, entry = nxtomomill_converter.from_edf_to_nx(
            configuration=config, progress=self.progress
        )
        scan = NXtomoScan(entry=entry, scan=file_path)
        if self.get_input_value("serialize_output_data", True):
            self.outputs.data = scan.to_dict()
        else:
            self.outputs.data = scan

    @staticmethod
    def deduce_output_file_path(
        folder_path, output_dir: ProcessDataOutputDirMode | str, scan
    ):
        try:
            output_dir = ProcessDataOutputDirMode.from_value(output_dir)
        except Exception:
            pass

        if output_dir is ProcessDataOutputDirMode.OTHER:
            raise ValueError("if mode is other, we expect 'output_dir' to be the path")
        elif output_dir in (None, ProcessDataOutputDirMode.IN_SCAN_FOLDER):
            output_folder = os.path.dirname(folder_path)
        elif output_dir is ProcessDataOutputDirMode.PROCESSED_DATA_FOLDER:
            path = pathlib.Path(get_default_output_file(folder_path))
            output_folder = str(path.parent)
        else:
            # else we expect people to provide output location
            output_folder = format_output_location(output_dir, scan=scan)
        return os.path.join(output_folder, os.path.basename(folder_path) + ".nx")


def get_default_raw_data_output_file(
    input_file: str, output_file_extension: str = ".nx"
) -> str:
    """
    Policy: look for any 'RAW_DATA' in file directory. If find any (before any 'PROCESSED_DATA' directory) replace it "RAW_DATA".
    Then replace input_file by the expected file_extension and make sure the output file is different than the input file. Else append _nxtomo to it.

    :param input_file: file to be converted from bliss to NXtomo
    :param output_file_extension:
    :return: default output file according to policy
    """
    if isinstance(input_file, pathlib.Path):
        input_file = str(input_file)
    if not isinstance(input_file, str):
        raise TypeError(
            f"input_file is expected to be an instance of str. {type(input_file)} provided"
        )
    if not isinstance(output_file_extension, str):
        raise TypeError("output_file_extension is expected to be a str")
    if not output_file_extension.startswith("."):
        output_file_extension = "." + output_file_extension

    input_file = os.path.abspath(input_file)
    input_file_no_ext, _ = os.path.splitext(input_file)

    output_path = to_raw_data_path(input_file_no_ext)
    output_file = output_path + output_file_extension
    if output_file == input_file:
        # to be safer if the default output file is the same as the input file (if the input file has a .nx extension and not in any 'RAw_DATA' directory)
        return output_path + "_nxtomo" + output_file_extension
    else:
        return output_file
