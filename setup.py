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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    install_requires=[
        'Pillow~=9.2.0',
        'pyaml~=21.10.1',
        'click~=8.1.3',
    ],
    entry_points={
        'console_scripts': [
            'stawp = stawp.cli:cli'
        ],
    },
)

