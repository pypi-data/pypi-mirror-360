from contextlib import contextmanager

from silx.gui import qt

if qt.BINDING == "PyQt5":
    from PyQt5.QtTest import QSignalSpy  # pylint: disable=E0401,E0611
elif qt.BINDING == "PySide6":
    from PySide6.QtTest import QSignalSpy  # pylint: disable=E0401,E0611
elif qt.BINDING == "PyQt6":
    from PyQt6.QtTest import QSignalSpy  # pylint: disable=E0401,E0611
else:
    QSignalSpy = None


@contextmanager
def block_signals(w: qt.QWidget):
    old = w.blockSignals(True)
    try:
        yield
    finally:
        w.blockSignals(old)
