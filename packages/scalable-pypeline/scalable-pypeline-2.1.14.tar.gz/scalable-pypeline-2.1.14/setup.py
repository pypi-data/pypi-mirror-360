"""PypeLine Library Setup"""

import re
import ast
import sys
import os
from typing import List

from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """PyTest Command"""

    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import coverage
        import pytest

        if self.pytest_args and len(self.pytest_args) > 0:
            self.test_args.extend(self.pytest_args.strip().split(" "))
            self.test_args.append("tests/")

        cov = coverage.Coverage()
        cov.start()
        errno = pytest.main(self.test_args)
        cov.stop()
        cov.report()
        cov.html_report()
        print("Wrote coverage report to htmlcov directory")
        sys.exit(errno)


# Defaults that will be overridden/updated if do_cythonize is true.
#
ext_modules = []
cmdclass = {"test": PyTest}
packages = find_packages(exclude=["tests"])

do_cythonize = os.getenv("CYTHONIZE", "false").lower() == "true"
if do_cythonize:
    try:
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext

        cmdclass["build_ext"] = build_ext  # Use cython's build_ext

        def scandir(
            directory: str,
            exclude_paths: List[str] = None,
            paths: List[str] = None,
            directories: List[str] = None,
            return_directories: bool = False,
            recursive: bool = True,
        ):
            """Scan a given directory recursively and produce a list
            of file paths (e.g. ['pypeline/app.py', 'pypeline/config.py'])
            or directroies (e.g. ['pypeline/api', 'pypeline/utils'])
            """
            if paths is None:
                paths = []
            if directories is None:
                directories = []
            if exclude_paths is None:
                exclude_paths = []

            for file in os.listdir(directory):
                path = os.path.join(directory, file)
                if any([p in path for p in exclude_paths]):
                    continue

                if "__init__.py" in path or "__pycache__" in path:
                    continue

                if os.path.isfile(path) and path.endswith(".py"):
                    paths.append(path)
                elif os.path.isdir(path) and recursive:
                    directories.append(path)
                    scandir(
                        path,
                        exclude_paths=exclude_paths,
                        paths=paths,
                        directories=directories,
                        return_directories=return_directories,
                        recursive=recursive,
                    )

            if return_directories:
                return directories
            return paths

        def make_extension(ext_path: str):
            """Generate an Extension() object. Takes a path
            e.g. pypeline/app.py
            and generates a valid Extension
            e.g. Extension('pypeline.app', ['pypeline/app.py'])
            """
            extName = ext_path.replace("/", ".")[:-3]
            return Extension(extName, [ext_path], include_dirs=["."])

        to_cythonize = scandir(
            "pypeline",
            exclude_paths=[
                "pypeline/templates",
                "pypeline/static",
                "pypeline/celery.py",
                "pypeline/tools/thumbnail/thumbnail.py",
                "pypeline/lib/config_server.py",
            ],
        )

        ext_modules = cythonize(
            [make_extension(path) for path in to_cythonize], language_level=3
        )

        class MyBuildPy(build_py):
            """Update standard build_py to exclude any files we
            explicitly cythonize.
            """

            def find_package_modules(self, package, package_dir):
                """Return list of all package modules that are *not* cythonized
                for regular packaging.
                """
                modules = super().find_package_modules(package, package_dir)
                filtered_modules = []
                for tup in modules:
                    if tup[2] in to_cythonize:
                        continue
                    filtered_modules.append(tup)
                return filtered_modules

        cmdclass["build_py"] = MyBuildPy

    except ImportError:
        pass

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("pypeline/__init__.py", "rb") as f:
    __version__ = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

setup(
    name="scalable-pypeline",
    version=__version__,
    description="PypeLine - Python pipelines for the Real World",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Bravos Power Corporation",
    license="Apache License 2.0",
    url="https://gitlab.com/bravos2/pypeline",
    packages=packages,
    include_package_data=True,
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    install_requires=install_requires,
    extras_require={
        "build": ["wheel", "twine"],
        "flask": [
            "markupsafe==2.0.1",
            "flask-smorest>=0.23.0,<1",
        ],
        "web": ["gunicorn", "gevent>=21.12.0,<22"],
        "workers": [
            "networkx>=2.4",
            "dramatiq[rabbitmq]==1.17.0",
            "apscheduler>=3.10.4,<4",
            "tenacity==9.1.2",
        ],
        "dev": ["black"],
        "test": [
            "pytest-cov>=2.6.1,<3",
            "tox>=3.14.1,<4",
            "mock>=1,<2",
            "responses>=0.10.16,<0.11",
            "fakeredis>=2.10.3,<3",
        ],
    },
    entry_points={
        "flask.commands": [
            "pypeline-worker=pypeline.dramatiq:pypeline_worker",
            "cron-scheduler=pypeline.dramatiq:cron_scheduler",
        ]
    },
)
