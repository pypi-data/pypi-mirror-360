from setuptools import setup, find_packages

setup(
    name='kaqing',
    version='0.4',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'qing = walker.cli:cli'
        ]
    }
)
