from setuptools import setup, find_packages

setup(
    name="normalize_currency",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pandas", "forex-python"],
    author="Your Name",
    description="Normalize and convert mixed-currency columns in pandas using a simple accessor.",
    license="MIT",
    keywords="currency normalization pandas forex",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)