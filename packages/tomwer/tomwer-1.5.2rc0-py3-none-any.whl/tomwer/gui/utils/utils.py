"""
Some utils GUI associated to illustrations
"""

from __future__ import annotations
from silx.io.url import DataUrl


import logging
import os
import subprocess
import threading
import platform

_logger = logging.getLogger(__name__)


__has_image_j = None
__image_j_from = None

_IMAGE_J_BIN_PATH = "/sware/pub/ImageJ/ImageJ"


def has_imagej():
    """Return if imagej command is accessible from the computer"""
    global __has_image_j
    global __image_j_from
    if __has_image_j is None:
        if platform.machine() in ("x86_64", "AMD64") and os.path.exists(
            _IMAGE_J_BIN_PATH
        ):
            __image_j_from = "binary"
            __has_image_j = True
        else:
            try:
                # use help because there is no information regarding version
                subprocess.call(["imagej", "-h"], stdout=subprocess.PIPE)
            except Exception:
                __has_image_j = False
            else:
                __image_j_from = "command"
                __has_image_j = True
    return __has_image_j


def open_url_with_image_j(url: DataUrl) -> threading.Thread:
    """open the url in an imagej subprocess within a thread.
    It is up to the caller to handle thread life

    :param url: url we want to open in imagej
    """
    global __image_j_from  # noqa: F824
    if not has_imagej():
        raise OSError("ImageJ is not installed")
    thread = ImageJthread(url=url, image_j_from=__image_j_from)
    thread.start()
    return thread


class ImageJthread(threading.Thread):
    def __init__(self, url, image_j_from, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._image_j_from = image_j_from
        self._url = url
        self._process = None

    def run(self):
        if self._image_j_from == "command":
            # for now we only manage the simple case of an edf file
            try:
                self._process = subprocess.Popen(
                    ["imagej", "-o", self._url.file_path()],
                )
            except Exception as e:
                _logger.warning(f"Fail to open {self._url}. Reason is {e}")
            else:
                self._process.communicate()

        elif self._image_j_from == "binary":
            try:
                self._process = subprocess.Popen(
                    [_IMAGE_J_BIN_PATH, self._url.file_path()],
                )
            except Exception as e:
                _logger.warning(f"Fail to open {self._url}. Reason is {e}")
            else:
                self._process.communicate()

    def quit(self):
        if self._process is not None:
            self._process.kill()
            self._process.wait()
