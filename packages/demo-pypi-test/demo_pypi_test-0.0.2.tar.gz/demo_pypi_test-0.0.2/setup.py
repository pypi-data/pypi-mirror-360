from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='demo_pypi_test',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        # 'requests',  # Example dependency
    ],
    author='Agnish Choudhury',
    entry_points={
        "console_scripts": [
            "hello=demo_pypi_test.main:hello",
        ]
    }
)