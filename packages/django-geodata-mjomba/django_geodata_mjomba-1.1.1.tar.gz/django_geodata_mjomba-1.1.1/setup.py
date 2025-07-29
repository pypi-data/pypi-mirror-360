from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-geodata-mjomba',
    version='1.1.1',  # Updated version number
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=3.2',
    ],
    python_requires='>=3.7',  # Specify minimum Python version
    author='Norman Mjomba',
    author_email='mjomban@gmail.com',
    description='A Django package for geographical data (regions, subregions, countries, states, cities)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mjombanorman/django-geodata.git',
    project_urls={
        'Bug Tracker': 'https://github.com/mjombanorman/django-geodata/issues',
        'Source Code': 'https://github.com/mjombanorman/django-geodata',
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # SPDX-License-Identifier: MIT
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
