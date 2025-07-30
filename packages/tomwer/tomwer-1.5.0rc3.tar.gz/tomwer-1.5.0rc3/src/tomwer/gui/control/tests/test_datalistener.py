# coding: utf-8
from __future__ import annotations

import pytest
from silx.gui import qt
from silx.gui.utils.testutils import SignalListener, TestCaseQt

from tomwer.gui.control.datalistener import ConfigurationWidget
from tomwer.tests.utils import skip_gui_test


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDataListenerConfiguration(TestCaseQt):
    """
    Simple test the interface for configuration is working
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
        self.qapp.processEvents()
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

    def testInteraction(self):
        """make sure the sigConfigurationChanged is emitted only when the
        user validate the modifications. This is done because we need to
        stop the thread and launch a new one, we don't wan't to do this
        automatically"""
        self._configWidget.setPort(4000)
        self._configWidget.setHost("tata")
        self.assertEqual(self.sig_listener.callCount(), 0)
        self._configWidget.validate()
        self.qapp.processEvents()
        self.assertEqual(self.sig_listener.callCount(), 1)
