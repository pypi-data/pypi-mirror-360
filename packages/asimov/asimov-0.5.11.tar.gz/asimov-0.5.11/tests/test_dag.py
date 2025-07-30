import os
import shutil
import unittest

import click

import asimov.event
from asimov.ledger import YAMLLedger
from asimov.cli.project import make_project
from asimov.cli.application import apply_page
import git


TEST_LEDGER = """

"""

class DAGTests(unittest.TestCase):
    """All the tests to check production DAGs are generated successfully."""
    @classmethod
    def setUpClass(cls):
        cls.cwd = os.getcwd()
    
    @classmethod
    def tearDownClass(cls):
        """Destroy all the products of this test."""
        os.chdir(cls.cwd)

    def setUp(self):
        os.makedirs(f"{self.cwd}/tests/tmp/project")
        os.chdir(f"{self.cwd}/tests/tmp/project")
        make_project(name="Test project", root=f"{self.cwd}/tests/tmp/project")
        self.ledger = YAMLLedger(f".asimov/ledger.yml")
        apply_page(file = "https://git.ligo.org/asimov/data/-/raw/main/defaults/production-pe.yaml", event=None, ledger=self.ledger)
        apply_page(file = "https://git.ligo.org/asimov/data/-/raw/main/events/gwtc-2-1/GW150914_095045.yaml", event=None, ledger=self.ledger)
        
    def tearDown(self):
        shutil.rmtree(f"{self.cwd}/tests/tmp/project")
    
    def test_simple_dag(self):
        """Check that all jobs are run when there are no dependencies specified."""
        apply_page(file = f"{self.cwd}/tests/test_data/test_simple_dag.yaml", event='GW150914_095045', ledger=self.ledger)
        event = self.ledger.get_event('GW150914_095045')[0]
        self.assertEqual(len(event.get_all_latest()), 2)
    
    def test_linear_dag(self):
        """Check that all jobs are run when the dependencies are a chain."""
        apply_page(file = f"{self.cwd}/tests/test_data/test_linear_dag.yaml", event='GW150914_095045', ledger=self.ledger)
        event = self.ledger.get_event('GW150914_095045')[0]
        self.assertEqual(len(event.get_all_latest()), 1)
        

    def test_complex_dag(self):
        """Check that all jobs are run when the dependencies are not a chain."""

        apply_page(file = f"{self.cwd}/tests/test_data/test_complex_dag.yaml", event='GW150914_095045', ledger=self.ledger)
        event = self.ledger.get_event('GW150914_095045')[0]
        self.assertEqual(len(event.get_all_latest()), 2)
