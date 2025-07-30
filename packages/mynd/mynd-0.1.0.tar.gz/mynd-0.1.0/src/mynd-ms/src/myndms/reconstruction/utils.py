"""Module for utility functionality for the reconstruction package."""

import math
import os
import sys

from collections.abc import Callable
from contextlib import contextmanager

import tqdm

from mynd.utils.log import logger

from .types import ProgressCallback


def create_progress_callback_percent(progress_bar: tqdm.tqdm) -> ProgressCallback:
    """Creates a callback for the given progress bar."""

    def update_progress_percent(percent: float) -> None:
        """Updates a progress bar to the given percentage."""
        previous: float = progress_bar.n
        increment: float = percent - previous

        if math.isnan(increment):
            increment: float = 0.0

        progress_bar.update(increment)

    return update_progress_percent


def progress_bar(description: str) -> Callable:
    """Calls a function with a progress bar."""

    def decorator(func: Callable) -> Callable:
        """Decorator function for adding a progress bar."""

        def wrapper(*args, **kwargs) -> None:
            """Wrapper function."""
            with tqdm.tqdm(total=100) as progress_bar:
                progress_bar.set_description(description)
                callback: ProgressCallback = create_progress_callback_percent(
                    progress_bar
                )
                func(*args, **kwargs, progress_fun=callback)

        return wrapper

    return decorator


@contextmanager
def stdout_redirected(sink_path: str = os.devnull):
    """Redirects the stdout sink to the given file descriptor within a context,
    before restoring it to the original descriptor.

    Adapted from:
    https://stackoverflow.com/questions/5081657/how-do-i-prevent-a-c-shared-library-to-print-on-stdout-in-python/17954769#17954769

    Example usage:
    import os

    with stdout_redirected(to=filename):
        print("from Python")
        os.system("echo non-Python applications are also supported")
    """
    old_file_descriptor = sys.stdout.fileno()

    #### # assert that Python and C stdio write using the same file descriptor
    #### assert libc.fileno(ctypes.c_void_p.in_dll(libc, "stdout")) == fd == 1

    def _redirect_stdout(sink_path: str):
        """TODO"""
        sys.stdout.close()  # + implicit flush()
        os.dup2(sink_path.fileno(), old_file_descriptor)  # fd writes to 'to' file
        sys.stdout = os.fdopen(old_file_descriptor, "w")  # Python writes to fd

    with os.fdopen(os.dup(old_file_descriptor), "w") as old_stdout:
        with open(sink_path, "w") as file:
            _redirect_stdout(sink_path=file)
        try:
            yield  # allow code to be run with the redirected stdout
        finally:
            # restore stdout, buffering and flags such as, CLOEXEC may be different
            _redirect_stdout(sink_path=old_stdout)
