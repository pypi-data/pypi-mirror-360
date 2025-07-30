from .data import test_job

from usdol_wage_determination_model import Job


def test_basic():
    job = Job(**test_job)
    assert job.classification == test_job['classification']
