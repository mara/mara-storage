from setuptools import setup, find_packages
import re

def get_long_description():
    with open('README.md') as f:
        return re.sub('!\[(.*?)\]\(docs/(.*?)\)', r'![\1](https://github.com/mara/mara-storage/raw/master/docs/\2)', f.read())

about = {}
with open('mara_storage/_version.py') as f:
    exec(f.read(), about)

setup(
    name='mara-storage',
    version=about['__version__'],

    description='Configuration of storage connections for mara',

    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    url = 'https://github.com/mara/mara-storage',
    project_urls={
        'Source Code': 'https://github.com/mara/mara-storage',
    },

    install_requires=[
        'click'
    ],
    python_requires='>=3.6',

    extras_require={
        'test': ['pytest'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={}
)