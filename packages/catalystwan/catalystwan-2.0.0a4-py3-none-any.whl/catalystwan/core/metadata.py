import multiprocessing
from functools import lru_cache, wraps
from importlib import metadata
from importlib.machinery import PathFinder
from pathlib import Path
from traceback import FrameSummary, StackSummary, extract_stack
from typing import Callable, List, Optional

PACKAGE_NAME = "catalystwan"
PACKAGE_VERSION = metadata.version(PACKAGE_NAME)
USER_AGENT = f"{PACKAGE_NAME}/{PACKAGE_VERSION}"


def with_proc_info_header(method: Callable[..., str]) -> Callable[..., str]:
    """
    Adds process ID and external caller information before first line of returned string
    """

    @wraps(method)
    def wrapper(*args, **kwargs) -> str:
        wrapped = method(*args, **kwargs)
        header = f"{multiprocessing.current_process()}"
        if frame_summary := get_first_external_stack_frame(extract_stack()):
            fname, line_no, function, _ = frame_summary
            header += " %s:%d %s(...)" % (fname, line_no, function)
        header += "\n"
        return header + wrapped

    return wrapper


def get_first_external_stack_frame(stack: StackSummary) -> Optional[FrameSummary]:
    """
    Get the first python frame
    on the stack before entering catalystwan module
    """
    if len(stack) < 1:
        return None
    for index, frame in enumerate(stack):
        if is_file_in_package(frame.filename):
            break
    if index == 0:
        return None
    return stack[index - 1]


@lru_cache()
def is_file_in_package(fname: str) -> bool:
    """
    Checks if filepath given by string
    is part of catalystwan source code
    """
    return Path(fname) in pkg_src_list


def list_package_sources(package: Optional[str] = None) -> List[Path]:
    """
    Creates a list containing paths to all python source files
    for current package
    """
    if package is None:
        package = __package__
    pkg_srcs: List[Path] = []
    if pkg_spec := PathFinder.find_spec(package):
        if pkg_origin := pkg_spec.origin:
            pkg_srcs = list(Path(pkg_origin).parent.glob("**/*.py"))
    return pkg_srcs


pkg_src_list = list_package_sources(PACKAGE_NAME)
