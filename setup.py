"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='bloom',
    version='0.3.0',
    description='Blog output manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nettee/bloom',
    author='nettee',
    author_email='nettee.liu@gmail.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='markdown',
    project_urls={
        'Source': 'https://github.com/nettee/bloom',
    },
    packages=find_packages(),
    install_requires=[
        'fire',
        'toml',
        'pytest',
        'pyperclip',
        'dacite',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'bloom=bloom:main',
        ],
    },
)
