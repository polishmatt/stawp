from setuptools import setup
import importlib

config = importlib.import_module('stawp.config')

setup(
    name='stawp',
    version=config.version,
    install_requires=[
        'Pillow==2.3.0',
        'pyaml==15.8.2',
        'click==6.6'
    ],
    entry_points={
        'console_scripts': [
            'stawp = stawp.cli:cli'
        ],
    },
)

