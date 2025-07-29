from setuptools import setup, find_packages

setup(
    name="lightimpact",
    version="0.1.3",
    description="LightImpact – Python tool to calculate Energy Reduction Value (ERV) for ICVs and EVs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Suzana Ostojic",
    author_email="suzana.ostojic@inab.rwth-aachen.de",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    python_requires=">=3.7",
)