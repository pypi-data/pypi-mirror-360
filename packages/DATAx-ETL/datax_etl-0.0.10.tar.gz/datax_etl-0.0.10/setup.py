from setuptools import setup, find_packages
setup(
    name='DATAx-ETL',
    version='0.0.10',
    author='Almir J Gomes',
    author_email='almir.jg@hotmail.com',
    packages=find_packages(),
    install_requires=[
        "DE_Lib>=0.0.49.1"
    ],
    python_requires='>=3.9',
    description="APP de EXTRACT  do ETL da suite DATAx",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/DE-DataEng/DATAx-ETL.git',
)