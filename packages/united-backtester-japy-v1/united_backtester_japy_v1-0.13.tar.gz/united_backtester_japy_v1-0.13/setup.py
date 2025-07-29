# hamoni/setup.py
from setuptools import setup, find_packages

setup(
    name="united_backtester_japy_v1",
    version="0.13",
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
