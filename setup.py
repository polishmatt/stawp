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
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'Pillow>=6.2.1,<6.999.999',
        'pyaml>=19.12.0,<19.999.999',
        'click>=6.6,<6.999.999'
    ],
    entry_points={
        'console_scripts': [
            'stawp = stawp.cli:cli'
        ],
    },
)

