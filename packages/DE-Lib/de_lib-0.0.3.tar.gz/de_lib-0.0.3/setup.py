from setuptools import setup, find_packages
setup(
    name='DE_Lib',
    version='0.0.3',
    author='Almir J Gomes',
    author_email='almir.jg@hotmail.com',
    packages=find_packages(),
    install_requires=[
        "DE_Lib>=0.0.49.1",
    ],
    python_requeries=">=3.9",
    description="Biblioteca de funcionalidades",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/DE-DataEng/DATAx-ETL.git',
)