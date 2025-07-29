"""Useful decorators for research methods."""

from datetime import datetime


def experiment(function):
    """Decorator to mark a function as an experiment."""

    def wrapper(*args, **kwargs):
        print(
            "\n"
            "===== STARTING EXPERIMENT "
            f"== {function.__name__} "
            f"== {datetime.now().isoformat()} ====="
        )
        result = function(*args, **kwargs)
        print(
            "===== FINISHED EXPERIMENT "
            f"== {function.__name__} "
            f"== {datetime.now().isoformat()} ====="
            "\n"
        )
        return result

    return wrapper
