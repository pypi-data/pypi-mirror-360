"""
Setup script for django-gradual-throttle.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='django-gradual-throttle',
    version='1.0.3',
    description='Django middleware for gradual request throttling with configurable delay strategies',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Dhruv Patel',
    author_email='pateldhruvn2004@gmail.com',
    url='https://github.com/Dhruvpatel004/django-gradual-throttle',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
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
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django middleware throttling rate-limiting gradual delay',
    project_urls={
        'Bug Reports': 'https://github.com/Dhruvpatel004/django-gradual-throttle/issues',
        'Source': 'https://github.com/Dhruvpatel004/django-gradual-throttle',
        'Documentation': 'https://github.com/Dhruvpatel004/django-gradual-throttle#readme',
    },
)
