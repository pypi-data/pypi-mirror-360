from setuptools import setup, find_packages

setup(
    name='some_pypi_package',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add dependencies here.
        # e.g. 'numpy>=1.11.1'
    ],
    entry_points={
        "console_scripts": [
            "some-pypi-package = some_pypi_package:hello",
        ]
    }
)
