import os
import sys
import codecs
import favicon

from distutils.core import setup
from setuptools import setup, find_packages

version = favicon.__version__

setup(
    name='django-favicon-plus-reloaded',
    version=version,
    url='https://edugit.org/AlekSIS/libs/django-favicon-plus',
    packages=find_packages(),
    license='MIT',
    description='Simple Django app which allows you to upload a image and it renders a wide variety for html link tags to display the favicon',
    long_description=codecs.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=open('requirements.txt').read().split('\n'),
    author='arteria GmbH',
    author_email='arteria@arteria.ch',
    maintainer='AlekSIS Team',
    maintainer_email='aleksis-dev@lists.teckids.org',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    zip_safe=False
)
