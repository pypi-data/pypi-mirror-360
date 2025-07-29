#!/usr/bin/env python

"""Tests for `pitrading` package."""


from datetime import timedelta
import unittest

import pandas as pd

from pitrading import pitrading
from pitrading.holidays import Holidays
from pitrading.instrument import Instrument

class TestPitrading(unittest.TestCase):
    """Tests for `pitrading` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""
        Instrument('20220724', suffix='8am').get_contract_mapping()
        Instrument('20220724', suffix='com').get_contract_mapping()
        Instrument('20220724', suffix='prod').get_contract_mapping()
        Instrument('20220724', suffix='pi_sim').get_contract_mapping()
        Instrument('20220724', suffix='hilvg').get_contract_mapping()
        Instrument('20220724', suffix='csi').get_contract_mapping()
            
        