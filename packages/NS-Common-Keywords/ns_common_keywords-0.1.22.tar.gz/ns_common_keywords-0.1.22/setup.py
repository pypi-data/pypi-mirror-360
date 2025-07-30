from setuptools import setup, find_packages

setup(
    name='NS_Common_Keywords',
    version='0.1.22',
    author='Erik ten Asbroek',
    packages=find_packages(),
    install_requires=[
        'robotframework>=4.0.0',
        'robotframework-browser>=6.0.0',
        'faker>=18.0.0',
    ],
)