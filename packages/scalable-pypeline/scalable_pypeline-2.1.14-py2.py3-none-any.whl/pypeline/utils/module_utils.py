""" Utilities for loading modules/callables based on strings.
"""

import re
import logging
import importlib
from typing import Callable

logger = logging.getLogger(__name__)


class PypelineModuleLoader(object):
    """Helper class to load modules / classes / methods based on a path string."""

    def get_module(self, resource_dot_path: str):
        """Retrieve the module based on a 'resource dot path'.
        e.g. package.subdir.feature_file.MyCallable
        """
        module_path = ".".join(resource_dot_path.split(".")[:-1])
        module = importlib.import_module(module_path)
        return module

    def get_callable_name(self, resource_dot_path: str) -> str:
        """Retrieve the callable based on config string.
        e.g. package.subdir.feature_file.MyCallable
        """
        callable_name = resource_dot_path.split(".")[-1]
        return callable_name

    def get_callable(self, resource_dot_path: str) -> Callable:
        """Retrieve the actual handler class based on config string.
        e.g. package.subdir.feature_file.MyCallable
        """
        module = self.get_module(resource_dot_path)
        callable_name = self.get_callable_name(resource_dot_path)
        return getattr(module, callable_name)


def normalized_pkg_name(pkg_name: str, dashed: bool = False):
    """We maintain consistency by always specifying the package name as
    the "dashed version".

    Python/setuptools will replace "_" with "-" but resource_filename()
    expects the exact directory name, essentially. In order to keep it
    simple upstream and *always* provide package name as the dashed
    version, we do replacement here to 'normalize' both versions to
    whichever convention you need at the time.

    if `dashed`:
        my-package-name --> my-package-name
        my_package_name --> my-package-name

    else:
        my-package-name --> my_package_name
        my_package_name --> my_package_name
    """
    if dashed:
        return str(pkg_name).replace("_", "-")
    return str(pkg_name).replace("-", "_")


def match_prefix(string: str, prefix_p: str) -> bool:
    """For given string, determine whether it begins with provided prefix_p."""
    pattern = re.compile("^(" + prefix_p + ").*")
    if pattern.match(string):
        return True
    return False


def match_suffix(string: str, suffix_p: str) -> bool:
    """For given string, determine whether it ends with provided suffix_p."""
    pattern = re.compile(".*(" + suffix_p + ")$")
    if pattern.match(string):
        return True
    return False


def match_prefix_suffix(string: str, prefix_p: str, suffix_p: str) -> bool:
    """For given string, determine whether it starts w/ prefix & ends w/ suffix"""
    if match_prefix(string, prefix_p) and match_suffix(string, suffix_p):
        return True
    return False


def get_module(resource_dot_path: str):
    """Retrieve the module based on a 'resource dot path'.
    e.g. package.subdir.feature_file.MyCallable
    """
    module_path = ".".join(resource_dot_path.split(".")[:-1])
    module = importlib.import_module(module_path)
    return module


def get_callable_name(resource_dot_path: str) -> str:
    """Retrieve the callable based on config string.
    e.g. package.subdir.feature_file.MyCallable
    """
    callable_name = resource_dot_path.split(".")[-1]
    return callable_name


def get_callable(resource_dot_path: str) -> Callable:
    """Retrieve the actual handler class based on config string.
    e.g. package.subdir.feature_file.MyCallable
    """
    module = get_module(resource_dot_path)
    callable_name = get_callable_name(resource_dot_path)
    return getattr(module, callable_name)
