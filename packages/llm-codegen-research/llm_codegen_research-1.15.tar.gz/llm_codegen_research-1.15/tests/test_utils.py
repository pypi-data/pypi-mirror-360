"""Tests for various utility functions."""

import time

from llm_cgr import TimeoutException, experiment, timeout


def test_experiment_decorator(capfd):
    """
    Test the experiment decorator.
    """

    @experiment
    def sample_experiment():
        return "Experiment completed"

    result = sample_experiment()
    assert result == "Experiment completed"

    # capture the output
    captured = capfd.readouterr()
    output = captured.out.strip().split("\n")

    # check the start and end messages
    assert output[0].startswith("===== STARTING EXPERIMENT")
    assert output[-1].startswith("===== FINISHED EXPERIMENT")
    assert len(output) == 2  # Only start and end messages should be printed


def test_timeout_context():
    """
    Test the timeout context manager.
    """
    with timeout(1):
        time.sleep(0.5)  # should complete fine

    try:
        with timeout(1):
            time.sleep(2)  # should raise TimeoutException
    except TimeoutException:
        pass  # expected
