from setuptools import setup, find_packages

setup(
    name='etiennevar',
    version="1.0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'etiennevar = etiennevar.cli:main',
        ],
    },
)

