from setuptools import setup, find_packages

setup(
    name='NS_Common_Keywords',
    version='0.1.10',
    author='Erik ten Asbroek',
    packages=find_packages(),
    install_requires=[
        'robotframework-browser>=6.0.0',
        'robotframework-faker>=5.0.0'
    ],
)