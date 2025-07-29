# hamoni/setup.py
from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name="united_backtester_japy_v1",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version="0.14",
    packages=find_packages(where="libraries"),
    package_dir={"": "libraries"},
    python_requires=">=3.7",
    install_requires=[
        "pandas",
        "numpy==1.26.4",
        "matplotlib",
        "requests",
        "python-binance",
        "openpyxl",
        "pandas_ta==0.3.14b0",
        "pytz",
        "tqdm",
        "xlsxwriter"
        
    ],
)
