from setuptools import find_packages
from setuptools import setup

setup(
    name="mdbt",
    version="0.4.28",
    description="A CLI tool to manage dbt builds with state handling and manifest management",
    author="Craig Lathrop",
    author_email="info@markimicrowave.com",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0,<9.0.0",
        "pyperclip>=1.8.0,<2.0.0",
        "snowflake-connector-python[pandas]>=3.11.0,<4.0.0",
        "python-dotenv>=1.0.0,<1.2.0",
        "openai>=1.35.0,<2.0.0",
        "sqlfluff==3.4.0",
        "sqlfluff-templater-dbt==3.4.0",
        "wordninja==2.0.0",
        "ruamel.yaml<0.18.0",
        "recce<=0.44.3",
    ],
    entry_points={
        "console_scripts": [
            "mdbt=mdbt.cmdline:mdbt",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
