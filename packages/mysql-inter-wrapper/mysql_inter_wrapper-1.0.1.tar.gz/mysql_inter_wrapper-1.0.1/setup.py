from setuptools import setup, find_packages

setup(
    name='mysql-inter-wrapper',
    version='1.0.1',
    description='A lightweight Python wrapper for MySQL CRUD operations with Pandas support.',
    author='Wilfred Kisitu',
    author_email='wkfinancials@gmail.com',
    packages=['mysql_inter_wrapper'],
    install_requires=[
        'mysql-connector-python',
        'pandas'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
