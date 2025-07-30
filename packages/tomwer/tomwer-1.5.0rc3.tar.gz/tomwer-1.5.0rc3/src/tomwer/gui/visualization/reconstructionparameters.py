from __future__ import annotations

import numpy
import logging
from silx.gui import qt
from tomwer.core.utils.char import BETA_CHAR, DELTA_CHAR

_logger = logging.getLogger(__name__)


class ReconstructionParameters(qt.QWidget):
    """
    display reconstruction parameters of a volume
    """

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QFormLayout())
        # method
        self._methodQLE = qt.QLineEdit("", self)
        self.layout().addRow("method", self._methodQLE)
        self._methodQLE.setReadOnly(True)
        # paganin
        self._paganinQLE = qt.QLineEdit("", self)
        self._paganinQLE.setReadOnly(True)
        self.layout().addRow("Phase method", self._paganinQLE)
        # delta beta
        self._deltaBetaLabel = qt.QLabel(" / ".join((DELTA_CHAR, BETA_CHAR)), self)
        self._deltaBetaQLE = qt.QLineEdit("", self)
        self._deltaBetaQLE.setReadOnly(True)
        self.layout().addRow(self._deltaBetaLabel, self._deltaBetaQLE)
        # sample_detector distance
        self._sampleDetectorDistanceQLE = qt.QLineEdit("", self)
        self._sampleDetectorDistanceQLE.setReadOnly(True)
        self.layout().addRow(
            "sample-detector distance (cm)", self._sampleDetectorDistanceQLE
        )
        # pixel size
        self._voxelSizeQLE = qt.QLineEdit("", self)
        self._voxelSizeQLE.setReadOnly(True)
        self.layout().addRow("voxel size (cm)", self._voxelSizeQLE)
        # cor
        self._corQLE = qt.QLineEdit("", self)
        self._corQLE.setReadOnly(True)
        self.layout().addRow("cor (absolute)", self._corQLE)
        # padding type
        self._paddingTypeQLE = qt.QLineEdit("", self)
        self._paddingTypeQLE.setReadOnly(True)
        self.layout().addRow("padding type", self._paddingTypeQLE)
        # half tomo
        self._halfTomoCB = qt.QCheckBox("", self)
        self._halfTomoCB.setEnabled(False)
        self.layout().addRow("half tomo", self._halfTomoCB)
        # fbp filter type
        self._fbpFilterQLE = qt.QLineEdit("", self)
        self._fbpFilterQLE.setReadOnly(True)
        self.layout().addRow("fbp filter", self._fbpFilterQLE)
        # log min clip
        self._minLogClipQLE = qt.QLineEdit("", self)
        self._minLogClipQLE.setReadOnly(True)
        self.layout().addRow("log min clip", self._minLogClipQLE)
        # log max clip
        self._maxLogClipQLE = qt.QLineEdit("", self)
        self._maxLogClipQLE.setReadOnly(True)
        self.layout().addRow("log max clip", self._maxLogClipQLE)
        # sino normalization & normalization file
        self._sinonormalizationQLE = qt.QLabel("", self)
        self.layout().addRow("sino normalization", self._sinonormalizationQLE)
        self._sinonormalizationFileQLE = qt.QLabel("", self)
        self.layout().addRow("sino normalization file", self._sinonormalizationFileQLE)
        # software version
        self._softwareVersionQLE = qt.QLabel("", self)
        self.layout().addRow("software version", self._softwareVersionQLE)

        # Connect signal for paganinQLE
        self._paganinQLE.textChanged.connect(self._updateDeltaBetaVisibility)

    def _updateDeltaBetaVisibility(self):
        phase_method = self._paganinQLE.text()
        display_delta_beta = phase_method in ("paganin", "CTF")
        self._deltaBetaLabel.setVisible(display_delta_beta)
        self._deltaBetaQLE.setVisible(display_delta_beta)

    def setVolumeMetadata(self, metadata: dict | None):
        if metadata is None:
            metadata = {}
        elif not isinstance(metadata, dict):
            raise TypeError(f"url should be a {dict}. {type(metadata)} provided")

        for func in (
            self._setMethod,
            self._setPhaseMethod,
            self._setDeltaBeta,
            self._setDistance,
            self._setVoxelSize,
            self._setCor,
            self._setPaddingType,
            self._setHalfTomo,
            self._setFBPFilter,
            self._setMinLogClip,
            self._setMaxLogClip,
            self._setSinoNormalization,
            self._setSoftwareVersion,
        ):
            try:
                func(metadata)
            except Exception as e:
                _logger.warning(f"Fail update when call {func}. Error is", e)

    def _setMethod(self, metadata: dict):
        method = (
            metadata.get("nabu_config", {}).get("reconstruction", {}).get("method", "")
        )
        self._methodQLE.setText(method)

    def _setPhaseMethod(self, metadata: dict):
        phase_method = (
            metadata.get("nabu_config", {}).get("phase", {}).get("method", "")
        )
        # note: pahse method is expected to be in ("", "paganin", "CTF")
        self._paganinQLE.setText(phase_method)

    def _setDeltaBeta(self, metadata: dict):
        delta_beta = (
            metadata.get("nabu_config", {}).get("phase", {}).get("delta_beta", "")
        )
        self._deltaBetaQLE.setText(str(delta_beta))

    def _setDistance(self, metadata: dict):
        distance_cm = (
            metadata.get("processing_options", {})
            .get("phase", {})
            .get("distance_cm", None)
        ) or metadata.get("processing_options", {}).get("reconstruction", {}).get(
            "sample_detector_dist", None
        )
        if distance_cm not in (None, "", "None"):
            distance_cm = float(distance_cm)
            distance_cm = f"{distance_cm:.2}"
        else:
            distance_cm = ""
        self._sampleDetectorDistanceQLE.setText(distance_cm)

    def _setVoxelSize(self, metadata: dict):
        # voxel size can be stored as pixel size (old version) or voxel size (new version)
        recons_params = metadata.get("processing_options", {}).get("reconstruction", {})
        voxel_size_cm = recons_params.get("voxel_size_cm", [None] * 3)
        # back compatibility when voxel was a scalar ( ~ nabu 2023 ?)
        if numpy.isscalar(voxel_size_cm):
            voxel_size_cm = [voxel_size_cm] * 3

        # now voxel size is expected to be a tuple of three elements
        if voxel_size_cm is not None:

            def clean_voxel_value(value):
                if isinstance(value, str):
                    for char_to_ignore in (" ", "(", ")", "[", "]"):
                        value = value.replace(char_to_ignore, "")
                return value

            voxel_size_cm = [clean_voxel_value(value) for value in voxel_size_cm]

        else:
            # backward compatibility with old volume
            voxel_size_cm = recons_params.get("pixel_size_cm", [None] * 3)

        voxel_size_cm = filter(None, voxel_size_cm)

        def cast_voxel_value(value: float | None):
            return f"{float(value):.8}"

        voxel_size_cm = [cast_voxel_value(value) for value in voxel_size_cm]
        self._voxelSizeQLE.setText("x".join(voxel_size_cm))

    def _setCor(self, metadata: dict):
        cor = (
            metadata.get("processing_options", {})
            .get("reconstruction", {})
            .get("rotation_axis_position", None)
        )
        if cor not in (None, "None", "none"):
            cor = f"{float(cor):.2f}"
        else:
            cor = None
        self._corQLE.setText(cor if cor is not None else "")

    def _setPaddingType(self, metadata: dict):
        padding_type = (
            metadata.get("processing_options", {})
            .get("reconstruction", {})
            .get("padding_type", "")
        )
        self._paddingTypeQLE.setText(str(padding_type))

    def _setHalfTomo(self, metadata: dict):
        enable_halftomo = (
            metadata.get("processing_options", {})
            .get("reconstruction", {})
            .get("enable_halftomo", False)
        )
        self._halfTomoCB.setChecked(enable_halftomo in ("True", "true", True, 1, "1"))

    def _setFBPFilter(self, metadata: dict):
        fbp_filter_type = (
            metadata.get("processing_options", {})
            .get("reconstruction", {})
            .get("fbp_filter_type", "")
        )
        self._fbpFilterQLE.setText(str(fbp_filter_type))

    def _setMinLogClip(self, metadata: dict):
        log_min_clip = (
            metadata.get("processing_options", {})
            .get("take_log", {})
            .get("log_min_clip", "")
        )
        self._minLogClipQLE.setText(str(log_min_clip))

    def _setMaxLogClip(self, metadata: dict):
        log_max_clip = (
            metadata.get("processing_options", {})
            .get("take_log", {})
            .get("log_max_clip", "")
        )
        self._maxLogClipQLE.setText(str(log_max_clip))

    def _setSinoNormalization(self, metadata: dict):
        norm_method = (
            metadata.get("processing_options", {})
            .get("sino_normalization", {})
            .get("method", "")
        )
        sino_normalization_file = (
            metadata.get("nabu_config", {})
            .get("preproc", {})
            .get("sino_normalization_file", "")
        )

        self._sinonormalizationQLE.setText(norm_method)
        self._sinonormalizationFileQLE.setText(sino_normalization_file)
        self._sinonormalizationFileQLE.setToolTip(sino_normalization_file)

    def _setSoftwareVersion(self, metadata: dict):
        software_version = metadata.get("version", None) or metadata.get(
            "process_info", {}
        ).get("nabu_version", None)
        if software_version is None:
            software_version = ""

        software = "nabu"
        self._softwareVersionQLE.setText(f"{software} ({software_version})")
