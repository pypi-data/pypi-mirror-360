# coding: utf-8
from __future__ import annotations

import pytest
from silx.gui import qt
from silx.gui.utils.testutils import SignalListener, TestCaseQt

from tomwer.gui.control.datalistener import ConfigurationWidget
from tomwer.tests.utils import skip_gui_test


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestProcessManager(TestCaseQt):
    """
    Simple test on behavior of the ProcessManager
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self._configWidget = ConfigurationWidget(parent=None)
        self.sig_listener = SignalListener()
        self._configWidget.sigConfigurationChanged.connect(self.sig_listener)
        self._configWidget.setHost("localhost")

    def tearDown(self):
        self._configWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._configWidget.close()
        self._configWidget = None

    def testConfiguration(self):
        self.assertEqual(
            self._configWidget.getConfiguration(), {"host": "localhost", "port": 4000}
        )
        self._configWidget.setPort(0)
        self._configWidget.setHost("toto")
        self.assertEqual(
            self._configWidget.getConfiguration(), {"host": "toto", "port": 0}
        )
