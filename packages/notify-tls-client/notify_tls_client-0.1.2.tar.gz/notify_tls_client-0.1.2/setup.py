from setuptools import setup, find_packages

setup(
    name='notify_tls_client',
    version='0.7',
    packages=find_packages(),
    install_requires=[
        "dataclasses_json",
        "typing_extensions"
    ],
    author='Jeferson Albara',
    description='A custom TLS Client',
    include_package_data=True
)