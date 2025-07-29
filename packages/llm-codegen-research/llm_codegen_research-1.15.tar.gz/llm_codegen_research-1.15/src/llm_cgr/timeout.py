"""Context manager for handling timeouts."""

import contextlib
import signal


class TimeoutException(Exception):
    pass


@contextlib.contextmanager
def timeout(seconds: int):
    """
    Context manager that raises a TimeoutException if the block takes longer than the
    specified time.

    Uses signals, so it only works on Unix-like systems (Linux, macOS, etc.).
    """

    # function to execute when the timer expires
    def signal_handler(signum, frame):
        raise TimeoutException()

    signal.setitimer(signal.ITIMER_REAL, seconds)  # start timer
    signal.signal(signal.SIGALRM, signal_handler)  # set end of timer signal

    try:
        yield

    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)  # stop timer
