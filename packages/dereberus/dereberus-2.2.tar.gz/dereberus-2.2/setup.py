from setuptools import setup, find_packages # type: ignore
setup(
   name='dereberus',
   version='2.2',
   packages=find_packages(),
   install_requires=[
    'click',
    'tabulate',
    'pathlib',
    'requests'
   ],
   entry_points='''
    [console_scripts]
    dereberus=cli_bundle.cli:dereberus_commands
    ''',
)