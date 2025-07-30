# coding: utf-8
from __future__ import annotations


import os
import shutil
import tempfile
import unittest

import numpy

from tomwer.core.process.reconstruction.saaxis.params import SAAxisParams
from tomwer.core.process.reconstruction.saaxis.saaxis import SAAxisTask
from tomwer.core.process.reconstruction.scores.scores import (
    _METHOD_TO_FCT,
    compute_score_contrast_std,
)
from tomwer.core.utils.scanutils import MockNXtomo


class TestScoreFunctions(unittest.TestCase):
    """Test all the score functions"""

    def test_img_contrast_std_score(self):
        """simple test of the API to call compute_score_contrast_std"""
        data = numpy.random.random(100 * 100).reshape(100, 100)
        compute_score_contrast_std(data)

    def test_method_to_function(self):
        """Test the dictionary used to for linking the score method to the
        callback function"""
        data = numpy.random.random(100 * 100).reshape(100, 100)
        for method_name, fct in _METHOD_TO_FCT.items():
            with self.subTest(method_name=method_name, fct=fct):
                res = fct(data)
                self.assertFalse(res is None)
                self.assertTrue(isinstance(res, float))


class TestSAAxisProcess(unittest.TestCase):
    """Test the SAAxisProcess class"""

    def setUp(self) -> None:
        self.tempdir = tempfile.mkdtemp()
        dim = 10
        mock = MockNXtomo(
            scan_path=self.tempdir, n_proj=10, n_ini_proj=10, scan_range=180, dim=dim
        )
        mock.add_alignment_radio(index=10, angle=90)
        mock.add_alignment_radio(index=10, angle=0)
        self.scan = mock.scan

        self._default_saaxis_params = SAAxisParams()
        self._default_saaxis_params.output_dir = os.path.join(
            self.tempdir, "output_dir"
        )
        self._default_saaxis_params.slice_indexes = {"slice": 4}
        self._default_saaxis_params.nabu_config = {}
        self._default_saaxis_params.dry_run = True
        self._default_saaxis_params.file_format = "hdf5"

    def tearDown(self) -> None:
        shutil.rmtree(self.tempdir)

    def test(self):
        process = SAAxisTask(
            inputs={
                "data": self.scan,
                "sa_axis_params": self._default_saaxis_params.to_dict(),
                "serialize_output_data": False,
            }
        )

        self._default_saaxis_params.estimated_cor = 11
        self._default_saaxis_params.research_width = 2
        process = SAAxisTask(
            inputs={
                "data": self.scan,
                "sa_axis_params": self._default_saaxis_params.to_dict(),
                "serialize_output_data": False,
            },
        )
        process.run()
        process = SAAxisTask(
            inputs={
                "data": self.scan,
                "sa_axis_params": self._default_saaxis_params.to_dict(),
                "serialize_output_data": False,
            },
        )
        process.run()
