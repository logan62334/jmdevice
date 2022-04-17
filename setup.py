from setuptools import setup, find_packages

import jmdevice

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="jmdevice",
    version=jmdevice.__version__,
    description="jmdevice",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT Licence",
    author="mafei",
    url="https://github.com/logan62334/jmdevice.git",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    platforms="any",
    install_requires=[
        'tidevice'
    ]
)
