from setuptools import setup, find_packages

setup(
    name='wg_client_work',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'webdriver-manager',
    ],
)
