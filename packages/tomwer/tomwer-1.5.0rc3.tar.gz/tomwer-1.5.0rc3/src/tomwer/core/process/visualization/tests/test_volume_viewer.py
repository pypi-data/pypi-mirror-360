# coding: utf-8

from tomwer.core.process.visualization.volumeviewer import _VolumeViewerPlaceHolder


def test_volume_viewer():
    process = _VolumeViewerPlaceHolder(
        inputs={
            "data": None,
        }
    )
    process.run()
