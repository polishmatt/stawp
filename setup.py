
from setuptools import setup
import swp

setup(
    name='swp',
    version=swp.VERSION,
    install_requires=[
        'Pillow==2.3.0',
        'pyaml==15.8.2',
        'click==6.6'
    ],
    entry_points={
        'console_scripts': [
            'swp = swp:main'
        ],
    },
)

