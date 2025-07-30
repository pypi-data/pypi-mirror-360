from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("NectaPy/requirements.txt", "r", encoding="latin-1") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="NectaPy",
    version="0.11.0",
    author="Henrylee",
    author_email="henrydionizi@gmail.com",
    description="A Python package for accessing NECTA (National Examinations Council of Tanzania) results",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Henryle-hd/NectaPy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "beautifulsoup4>=4.12.3",
        "requests>=2.25.1"
    ],
    include_package_data=True,
    package_data={
        'NectaPy': ['supportingYear.txt'],
    }
)