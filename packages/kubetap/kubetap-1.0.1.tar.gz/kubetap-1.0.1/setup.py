
from setuptools import setup, find_packages

setup(
    name="kubetap",
    version="1.0.1",
    description="A CLI tool to tap into kubernetes clusters",
    author="Cosmin Drula",
    url="https://github.com/drulacosmin/kubetap",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
        "psutil",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "kubetap=kubetap.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
