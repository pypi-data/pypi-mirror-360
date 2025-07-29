"""
sagemaker_jupyterlab_extension setup
"""

import os
import json
import setuptools
from pathlib import Path

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
)

HERE = Path(__file__).parent.resolve()

# The name of the project
name = "sagemaker_jupyterlab_extension"

lab_path = HERE / name / "labextension"

labext_name = "@amzn/sagemaker-jupyterlab-extensions"

# Representative files that should exist after a successful build
ensured_targets = [str(lab_path / "package.json")]

# Extension data file or config to be included along with the extension package
# Extension data file includes basic metadata of the extension, default config
# of the extension and frontend UI assets
data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, str(lab_path), "**"),
    ("share/jupyter/labextensions/%s" % labext_name, str(HERE), "install.json"),
    (
        "etc/jupyter/jupyter_server_config.d",
        "jupyter-config/jupyter_server_config.d",
        "sagemaker_jupyterlab_extension.json",
    ),
    (".", str(HERE), "THIRD-PARTY-LICENSES"),
]

long_description = (HERE / "README.md").read_text()

# Get the package info from package.json
pkg_json = json.loads((HERE / "package.json").read_bytes())

package_data_spec = {name: ["*"]}

# Logic to build minified JupyterLab UI extension assets, using jupyter_packaging
# library
cmdclass = create_cmdclass(
    "jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec
)

cmdclass["jsdeps"] = combine_commands(
    install_npm(HERE, build_cmd="build:labextension", npm=["npm"]),
    ensure_targets(ensured_targets),
)

package_name_prefix = os.environ.get("PACKAGE_NAME_PREFIX", "")

setup_args = dict(
    name=f"{package_name_prefix}sagemaker-jupyterlab-extension",
    version=pkg_json["version"],
    url=pkg_json["homepage"],
    author=pkg_json["author"],
    description=pkg_json["description"],
    license=pkg_json["license"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    cmdclass=cmdclass,
    packages=setuptools.find_packages(),
    install_requires=[
        "jupyterlab>=4",
        "jupyter-events>=0.6.0",
        f"{package_name_prefix}sagemaker_jupyterlab_extension_common",
        "jupyterlab-git>=0.51.1,<1.0.0",
        "async-lru",
        "aws_embedded_metrics",
    ],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.9",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab4"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
    ],
    extras_require={
        "dev": [
            "pytest >= 6",
            "pytest-cov",
            "black",
            "pytest_jupyter",
        ]
    },
)

if __name__ == "__main__":
    setuptools.setup(**setup_args)
