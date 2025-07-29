from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dft-pipeline",
    version="0.3.5",
    author="Alexei Veselov",
    author_email="alexei.veselov92@gmail.com",
    description="Data Flow Tools - flexible ETL pipeline framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    keywords=["etl", "data-pipeline", "data-processing", "yaml", "analytics"],
    url="https://github.com/alexeiveselov92/dft",
    project_urls={
        "Homepage": "https://github.com/alexeiveselov92/dft",
        "Repository": "https://github.com/alexeiveselov92/dft",
        "Issues": "https://github.com/alexeiveselov92/dft/issues",
    },
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "pyarrow>=12.0.0",
        "jinja2>=3.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "dft=dft.cli.main:cli",
        ],
    },
)