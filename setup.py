from setuptools import setup
import importlib

config = importlib.import_module('stawp.config')

setup(
    name='stawp',
    version=config.version,
    description='STAtic Website Producer',
    author='Matt Wisniewski',
    author_email='stawp@mattw.us',
    license='MIT',
    url='https://github.com/polishmatt/stawp',
    packages=[
        'stawp',
        'stawp.modules',
    ],
    keywords=['static', 'website'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
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

