from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='datapipelab',
    version='0.3.6',
    description='A data pipeline library with connectors, sources, processors, and sinks.',
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'json5',
        'loguru',
        # 'azure-storage-blob',
        # 'google-cloud-storage',
        # 'pandas'
    ],
)