from setuptools import setup, find_packages
import os

# Read requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='fund_series_issue_audit',
    version='0.3.3',
    packages=find_packages(),
    install_requires=required,
    author='June Young Park',
    author_email='juneyoungpaak@gmail.com',
    description='A module for auditing and analyzing fund series issues',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.11',
    data_files=[('', ['requirements.txt'])],
)