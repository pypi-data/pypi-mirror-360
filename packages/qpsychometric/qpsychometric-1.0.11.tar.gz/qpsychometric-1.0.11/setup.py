from setuptools import setup, find_packages


# Read requirements.txt and store contents in a list
# with open("requirements.txt") as f:
#     required = f.read().splitlines()

setup(
name="qpsychometric",
version="1.0.11",
description="A Python package containing implemented psychometrics for LLMs.",
packages=find_packages(),
project_urls={
        "Academic Article": "https://openreview.net/pdf/026597881acf1899856edfa5147390a6a60bd3a8.pdf",
    },
classifiers=[
"Programming Language :: Python :: 3",
"License :: OSI Approved :: Apache Software License",
"Operating System :: OS Independent",
],
include_package_data=True,
python_requires=">=3.8",
install_requires=[
                'pandas==2.2.3',
                "qlatent>=1.0.11",
                "tqdm",
                "overrides",
                ]
)