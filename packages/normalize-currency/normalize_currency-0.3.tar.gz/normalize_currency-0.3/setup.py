from setuptools import setup, find_packages

# Load README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="normalize_currency",
    version="0.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pandas", "forex-python", "pycountry"],
    author="Usman Ghani",
    description="Normalize and convert mixed-currency columns in pandas using a simple accessor.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="currency normalization pandas forex",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
