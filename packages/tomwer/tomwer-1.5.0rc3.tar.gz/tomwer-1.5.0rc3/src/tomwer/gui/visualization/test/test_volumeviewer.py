import logging
import os
import pytest
import numpy
from time import sleep

from silx.gui import qt
from tomwer.core.volume.hdf5volume import HDF5Volume
from tomwer.core.volume.tiffvolume import TIFFVolume
from tomoscan.esrf.volume.tiffvolume import has_tifffile

from tomwer.tests.conftest import qtapp  # noqa F401
from tomwer.core.utils.scanutils import MockNXtomo
from tomwer.gui.visualization.volumeviewer import VolumeViewer

logging.disable(logging.INFO)


@pytest.mark.skipif(not has_tifffile, reason="tifffile not available")
def test_volume_viewer(
    qtapp,  # noqa F811
    tmp_path,
):
    """
    test the volume viewer setting a scan having an HDF5 volume linked to it
    """

    widget = VolumeViewer(parent=None)
    widget.setAttribute(qt.Qt.WA_DeleteOnClose)

    tmp_dir = tmp_path / "test_volume_viewer"
    tmp_dir.mkdir()

    # step 1 - test setting a scan containing a HDF5Volume
    scan = MockNXtomo(
        scan_path=os.path.join(str(tmp_dir), "myscan"),
        n_proj=20,
        n_ini_proj=20,
        dim=10,
    ).scan
    volume = HDF5Volume(
        file_path=os.path.join(scan.path, "volume.hdf5"),
        data_path="entry",
        data=numpy.random.random(60 * 10 * 10).reshape(60, 10, 10),
    )
    volume.save()

    scan.set_latest_vol_reconstructions(
        [
            volume,
        ]
    )

    widget.setScan(scan)
    assert widget._centralWidget.data() is not None
    widget.clear()
    assert widget._centralWidget.data() is None

    # step 2: test setting a a tiff volume dirrectly
    volume = TIFFVolume(
        folder=os.path.join(tmp_dir, "my_tiff_vol"),
        data=numpy.random.random(60 * 100 * 100).reshape(60, 100, 100),
    )
    volume.save()

    # 2.1 test with the data being in cache
    widget.setVolume(volume=volume)
    assert widget._centralWidget.data() is not None
    widget.clear()
    assert widget._centralWidget.data() is None

    # 2.2 test with the data not being in cache anymore
    volume.clear_cache()

    widget.setVolume(volume=volume)
    # wait_for_processing_finished
    while qt.QApplication.instance().hasPendingEvents():
        qt.QApplication.instance().processEvents()
    sleep(1.2)  # wait for the thread to be processed
    while qt.QApplication.instance().hasPendingEvents():
        qt.QApplication.instance().processEvents()
    # end waiting
    assert widget._centralWidget.data() is not None
