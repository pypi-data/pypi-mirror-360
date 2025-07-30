#!/usr/bin/env python
# on your machine, just run pytest in this directory or execute it to get outputs
#

import pytest

from a2p2.jmmc.models import _model


def test_same_blocks():
    """  duplicated blocks must have distinct computed names """
    m='[{ "type":"elong_gaussian", "flux_weight":1, "x":0, "y":0, "minor_axis_fwhm":1.234, "elong_ratio":1.2, "major_axis_pos_angle":45.6},{"type":"elong_gaussian", "flux_weight":1, "x":0, "y":0, "minor_axis_fwhm":1.234, "elong_ratio":1.2, "major_axis_pos_angle":45.6}]'
    xml_m=_model(m)
    assert "elong_gaussian2" in xml_m

