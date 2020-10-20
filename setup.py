from setuptools import setup, find_packages
import re

def get_long_description():
    with open('README.md') as f:
        return re.sub('!\[(.*?)\]\(docs/(.*?)\)', r'![\1](https://github.com/mara/mara-storage/raw/master/docs/\2)', f.read())

setup(
    name='mara-storage',
    version='0.9.0',

    description='Configuration of storage connections',

    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    url = 'https://github.com/mara/mara-storage',

    install_requires=[
        'click'
    ],
    python_requires='>=3.6',

    extras_require={
        'test': ['pytest'],
    },

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={}
)