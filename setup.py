import os
import re
import subprocess
from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__file_dir__ = Path(__file__).absolute().parent

local_patch_level = 0

tcl_version_define = re.compile(r"\#\s*define\s*TCL_(MAJOR|MINOR)_VERSION\s*(\d+)")
major = None
minor = None
with open(__file_dir__ / "tcl" / "generic" / "tcl.h", encoding="utf8") as f:
    for line in f:
        if match := tcl_version_define.search(line):
            if match[1] == "MAJOR":
                major = int(match[2])
            elif match[1] == "MINOR":
                minor = int(match[2])

version = f"{major}.{minor}.{local_patch_level}"

tcl = __file_dir__ / "tcl"
ext = Pybind11Extension(
    "minitcl._minitcl",
    ["src/main.cc"],
    include_dirs=[tcl / "generic"],
    extra_objects=[str(tcl / "libtcl9.1.a")],
)
ext.cxx_std = 17


class build_minitcl(build_ext):
    def build_extensions(self) -> None:
        # ensure tcl is built
        if not (tcl / "libtcl9.1.a").is_file():
            subprocess.check_call(
                [
                    tcl / "unix" / "configure",
                    "--disable-shared",
                    "--disable-zipfs",
                    # some distros lack zlib headers
                    f"CFLAGS=-I{tcl / 'compat' / 'zlib'}",
                ],
                cwd=tcl,
            )
            subprocess.check_call(
                ["make", f"-j{os.cpu_count() or 1}"],
                cwd=tcl,
            )
        super().build_extensions()

    def write_stub(self):
        subprocess.check_call(["pybind11-stubgen", "-o", ".", "minitcl._minitcl"])


setup(
    # getting the version programmatically: python3 -m build --metadata . | jq .version
    name="minitcl",
    packages=["minitcl"],
    version=version,
    description="Python wrapper around Yosys' libparse module",
    long_description=(__file_dir__ / "Readme.md").read_text(encoding="utf8"),
    long_description_content_type="text/markdown",
    author="Mohamed Gaber",
    author_email="me@donn.website",
    install_requires=["wheel"],
    python_requires=">=3.10",
    ext_modules=[ext],
    cmdclass={"build_ext": build_minitcl},
)
