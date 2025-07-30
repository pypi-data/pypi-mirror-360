"""contains QLFileSystem class. Specific implementation of the QLineEdit to select a file path."""

from silx.gui import qt


class QLFileSystem(qt.QLineEdit):
    """
    QLineEdit with a completer using a QDirModel
    """

    def __init__(self, text, parent, filters=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.completer = qt.QCompleter()
        model = qt.QDirModel(self.completer)
        if filters is not None:
            model.setFilter(filters)
        self.completer.setModel(model)
        self.setCompleter(self.completer)
        if text is not None:
            self.setText(text)
