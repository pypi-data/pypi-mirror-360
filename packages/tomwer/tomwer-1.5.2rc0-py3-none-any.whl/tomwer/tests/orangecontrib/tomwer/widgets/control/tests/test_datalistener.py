# coding: utf-8
from __future__ import annotations


import gc
import os
import pickle
import shutil
import tempfile
import time
from glob import glob

import pytest
from orangecanvas.scheme.readwrite import literal_dumps
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt

from orangecontrib.tomwer.widgets.control.DataListenerOW import DataListenerOW
from tomwer.core import settings
from tomwer.core.process.control.datalistener.rpcserver import BlissAcquisition
from tomwer.core.utils.scanutils import MockBlissAcquisition
from tomwer.tests.utils import skip_gui_test

try:
    from tomwer.synctools.rsyncmanager import RSyncManager  # noqa F401
except ImportError:
    has_rsync = False
else:
    has_rsync = RSyncManager().has_rsync()


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDataListenerSynchronization(TestCaseQt):
    """Insure synchronization is working with the orangecontrib widget"""

    def setUp(self):
        super().setUp()
        self._src_dir = tempfile.mkdtemp()
        self._dst_dir = tempfile.mkdtemp()
        # mock lbsram
        settings.mock_lsbram(True)
        settings._set_lbsram_path(self._src_dir)
        settings._set_dest_path(self._dst_dir)

        scan_path = os.path.join(self._src_dir, "scan0000")
        self.mock_scan = MockBlissAcquisition(
            n_sample=1,
            n_sequence=1,
            n_scan_per_sequence=3,
            n_darks=2,
            n_flats=2,
            output_dir=scan_path,
        )

        self.bliss_acquisition = BlissAcquisition(
            file_path=self.mock_scan.samples[0].sample_file,
            proposal_file=self.mock_scan.proposal_file,
            sample_file=self.mock_scan.samples[0].sample_file,
            entry_name="self.entry = '/1'",
            start_time=time.ctime(),
        )

        self.widget = DataListenerOW()

    def tearDown(self):
        self.mock_scan = None
        self.bliss_acquisition = None
        # self.widget.activate(False)
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.close()
        self.widget = None
        shutil.rmtree(self._src_dir)
        shutil.rmtree(self._dst_dir)
        gc.collect()

    @pytest.mark.skipif(not has_rsync, reason="rsync not installed")
    def testSynchronization(self):
        """Make sure the datalistener will launch a synchronization on the
        data dir when receive it"""
        self.assertEqual(len(os.listdir(self._dst_dir)), 0)
        self.widget.activate(True)

        self.widget.get_listening_thread()._rpc_sequence_started(
            saving_file=self.bliss_acquisition.sample_file,
            scan_title="toto",
            sequence_scan_number="1",
            proposal_file=self.bliss_acquisition.proposal_file,
            sample_file=self.bliss_acquisition.sample_file,
        )
        time.sleep(1.0)
        self.assertEqual(self.widget._get_n_scan_observe(), 1)
        self.assertEqual(len(os.listdir(self._dst_dir)), 1)
        self.widget.get_listening_thread()._rpc_sequence_ended(
            saving_file=self.bliss_acquisition.sample_file,
            sequence_scan_number="1",
            success=True,
        )
        nx_pattern = os.path.join(self.mock_scan.samples[0].sample_directory, "*.nx")
        self.assertEqual(len(glob(nx_pattern)), 0)
        for i in range(8):
            self.qapp.processEvents()
            time.sleep(1.0)
        # check .nx file has been created
        #
        self.assertEqual(len(glob(nx_pattern)), 1)

    def testSerialization(self):
        pickle.dumps(self.widget.get_configuration())

    def testLiteralDumps(self):
        literal_dumps(self.widget.get_configuration())
